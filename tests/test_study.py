import pytest

from crosswire.study import RunConfig, run, run_study, summarize


def test_configuration_rejects_nonfinite_unbounded_and_unknown_inputs():
    for values in ({'budget': True}, {'budget': -1}, {'horizon': 7}, {'seed': -1},
                   {'policy': 'secret_oracle'}, {'mystery': 2}, {'anchors': 'true'}):
        with pytest.raises(ValueError):
            RunConfig.from_dict(values)


def test_zero_budget_robust_refuses_semantically_ambiguous_connection():
    result = run(RunConfig(family='symmetric', budget=0))
    assert result['decision']['admitted'] is False
    assert result['audit']['contract_satisfied'] is None
    assert result['metrics']['target_steps'] == 0
    assert result['audit']['oracle_feasible'] is True
    assert result['decision_frozen_hash']


def test_anchors_and_probes_do_not_drop_true_map_on_supported_case():
    result = run(RunConfig(family='latch', budget=16, anchors=True))
    assert result['audit']['true_map_retained'] is True
    assert result['metrics']['target_steps'] <= 16
    assert result['metrics']['target_calls'] == result['metrics']['resets'] + result['metrics']['target_steps']
    if result['decision']['admitted']:
        assert result['audit']['contract_satisfied'] is True


def test_related_methods_share_probe_transcript_when_only_admission_changes():
    robust = run(RunConfig(family='latch', budget=8, admission='robust'))
    one = run(RunConfig(family='latch', budget=8, admission='one_best'))
    assert robust['probes'] == one['probes']


def test_semantic_corruption_uses_actual_private_events():
    oracle = run(RunConfig(family='semantic_corruption', admission='oracle', budget=0))
    assert oracle['baseline']['privileged'] is True
    assert oracle['audit']['contract_satisfied'] is True
    assert oracle['audit']['raw_equivalent_maps_count'] > 0


def test_summary_keeps_abstention_risk_undefined_and_clusters_related_cases():
    row = run(RunConfig(family='symmetric', budget=0))
    summary = summarize([row, row])[0]
    assert summary['requests'] == 2
    assert summary['parent_clusters'] == 1
    assert summary['selective_harm'] is None
    assert summary['useful_coverage'] == 0


def test_study_enforces_size_limit_before_work():
    with pytest.raises(ValueError):
        run_study({'seeds': list(range(10001))})


def test_calibration_budget_counts_resets_as_well_as_actions():
    result = run(RunConfig(family='symmetric', policy='fixed', budget=8))
    assert result['metrics']['target_calls'] <= 8


def test_failed_deployment_never_audits_an_unexecuted_suffix():
    result = run(RunConfig(family='malformed', seed=1, budget=0, admission='identity'))
    assert result['deployment']['complete'] is False
    assert result['audit']['semantic_events'] == []
    assert result['audit']['hazard'] is None
    summary = summarize([result])[0]
    assert summary['interface_errors'] == 1
    assert summary['hazardous'] == 0


def test_forced_fit_exposes_residual_instead_of_implying_consistency():
    result = run(RunConfig(family='incompatible', budget=16, policy='fixed', admission='fit'))
    fit = result['baseline']['fit_diagnostics']
    assert fit['chosen_adapter_id'] is not None
    assert fit['raw_mismatches'] > 0


def test_paired_comparison_never_matches_different_budget_conditions():
    from crosswire.study import paired_comparisons
    def row(policy, budget, success):
        return {'configuration': {'family':'latch','policy':policy,'admission':'robust',
                                  'seed':17,'budget':budget,'anchors':False,'horizon':4,
                                  'split':'evaluation','implementation':'procedural'},
                'parent_instance_id':'p1','audit':{'contract_satisfied':success}}
    assert paired_comparisons([row('task',4,True),row('random',8,False)]) == []


def test_paired_comparison_evaluates_admission_contrasts():
    from crosswire.study import paired_comparisons
    def row(admission, success):
        return {'configuration': {'family':'latch','policy':'task','admission':admission,
                                  'seed':17,'budget':4,'anchors':False,'horizon':4,
                                  'execution_mode':'shielded','temporal':False,
                                  'split':'evaluation','implementation':'procedural'},
                'parent_instance_id':'p1','audit':{'contract_satisfied':success}}
    pairs = paired_comparisons([row('robust', False), row('adaptive', True)])
    assert len(pairs) == 1
    assert pairs[0]['contrast'] == 'adaptive - robust'
    assert pairs[0]['mean_delta'] == 1.0


def test_unsupported_aalpy_combinations_rejected():
    from crosswire.study import RunConfig
    with pytest.raises(ValueError, match='AALpy baseline does not support temporal'):
        RunConfig(policy='aalpy', temporal=True).check()
    with pytest.raises(ValueError, match='AALpy baseline does not support adaptive'):
        RunConfig(policy='aalpy', admission='adaptive', execution_mode='shielded').check()


def _analysis_row(**changes):
    from dataclasses import asdict
    configuration = asdict(RunConfig())
    configuration.update(changes)
    return {'configuration': configuration, 'parent_instance_id': 'parent-latch',
            'decision': {'admitted': True, 'status': 'TASK_ADMISSIBLE'},
            'audit': {'contract_satisfied': True, 'oracle_feasible': True,
                      'hazard': False, 'calibration_hazardous_probes': 0},
            'metrics': {'target_calls': 0, 'target_steps': 0, 'resets': 0},
            'deployment': {'target_calls': 0}}


@pytest.mark.parametrize('field,other', [('anchors', True), ('split', 'evaluation'),
                                      ('horizon', 5), ('execution_mode', 'shielded'),
                                      ('temporal', True), ('escalate', True)])
def test_summary_separates_experimental_conditions(field, other):
    rows = [_analysis_row(), _analysis_row(**{field: other})]
    summary = summarize(rows)
    assert len(summary) == 2
    assert all(item['requests'] == 1 for item in summary)
    assert {item[field] for item in summary} == {rows[0]['configuration'][field], other}


def test_paired_comparison_never_matches_different_escalation_conditions():
    from crosswire.study import paired_comparisons
    rows = [_analysis_row(policy='task', escalate=True),
            _analysis_row(policy='random', escalate=False)]
    assert paired_comparisons(rows) == []


def test_paired_comparisons_report_separate_matching_condition_strata():
    from crosswire.study import paired_comparisons
    rows = [_analysis_row(policy=policy, escalate=escalate)
            for policy in ('task', 'random') for escalate in (False, True)]
    pairs = paired_comparisons(rows)
    assert len(pairs) == 2
    assert {pair['escalate'] for pair in pairs} == {False, True}
    assert all(pair['matched_cells'] == 1 for pair in pairs)


def test_paired_comparisons_reject_duplicate_cells_before_silent_overwrite():
    from crosswire.study import paired_comparisons
    first, duplicate = _analysis_row(), _analysis_row()
    duplicate['audit']['contract_satisfied'] = False
    with pytest.raises(ValueError, match='Duplicate'):
        paired_comparisons([first, duplicate, _analysis_row(policy='random')])


def test_model_escalation_preserves_discarded_class_computation_in_metrics():
    from crosswire.core import CandidateSpace
    from crosswire.fixtures import make_case, make_engine
    from crosswire.study import _acquire, fit_evidence
    case = make_case('delay', seed=17)

    def acquire(budget, escalate):
        engine, counts = make_engine(case.private), {'target_calls': 0}
        def query(word):
            engine.reset()
            counts['target_calls'] += 1 + len(word)
            return [engine.step(action) for action in word]
        result = _acquire(case.public, 'task', budget, query, counts, None, None,
                          escalate=escalate)
        engine.close()
        return result, counts['target_calls']

    (_, survivors, _, _, _), used = acquire(16, False)
    assert not survivors
    (static, _, probes, _, _), _ = acquire(used, False)
    (escalated, _, replayed, _, info), _ = acquire(used, True)
    assert replayed == [dict(probe, survivors_after=replayed[i]['survivors_after'])
                        for i, probe in enumerate(probes)]
    temporal = CandidateSpace(static.machine, static.contract, temporal=True)
    temporal.survivors(fit_evidence(probes), {})
    assert info['escalated'] is True
    assert escalated.work == {key: value + temporal.work[key]
                             for key, value in static.work.items()}

