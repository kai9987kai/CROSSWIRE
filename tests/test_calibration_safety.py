from copy import deepcopy
from dataclasses import asdict

import pytest

from crosswire.certificates import check_result
from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.fixtures import make_case, make_engine
from crosswire.study import RunConfig, _acquire, paired_comparisons, run, study_configs


@pytest.mark.parametrize('values', [
    {'probe_safety': 'secret'}, {'probe_safety': True},
    {'risk_tolerance': True}, {'risk_tolerance': '0.2'},
    {'risk_tolerance': float('nan')}, {'risk_tolerance': float('inf')},
    {'risk_tolerance': -0.1}, {'risk_tolerance': 1},
    {'risk_tolerance': 0.2}, {'probe_safety': 'model_safe', 'policy': 'aalpy'},
])
def test_configuration_rejects_invalid_safety_and_tolerance(values):
    with pytest.raises(ValueError):
        RunConfig.from_dict(values)


def test_safe_acquisition_abstains_without_dispatching_a_hazardous_probe():
    public = make_case('latch', 17).public
    counts = {'target_calls': 0}
    def forbidden_query(word):
        pytest.fail('All raw first actions have a hazardous surviving interpretation')
    _, survivors, probes, error, info = _acquire(
        public, 'fixed', 16, forbidden_query, counts, None, None, probe_safety='model_safe')
    assert len(survivors) == 144
    assert probes == [] and error is None and counts['target_calls'] == 0
    assert info['calibration']['stop_reason'] == 'NO_ELIGIBLE_SAFE_PROBE'


def test_safe_acquisition_with_anchors_records_each_preprobe_belief():
    case = make_case('routing', 17, anchors=True, horizon=4)
    engine, counts = make_engine(case.private), {'target_calls': 0}
    def query(word):
        engine.reset()
        counts['target_calls'] += 1 + len(word)
        return [engine.step(action) for action in word]
    try:
        space, survivors, probes, error, info = _acquire(
            case.public, 'entropy', 16, query, counts, None, None, probe_safety='model_safe')
    finally:
        engine.close()
    assert probes and error is None
    assert space.plan(survivors)['admitted']
    for probe in probes:
        assert probe['safety']['model_safe'] is True
        assert probe['safety']['candidate_count'] >= len(survivors)
    assert info['calibration']['mode'] == 'model_safe'


def test_safe_escalation_guards_the_enabled_temporal_envelope_before_promotion():
    case = make_case('routing', 17, anchors=True, horizon=4)
    engine, counts = make_engine(case.private), {'target_calls': 0}
    def query(word):
        engine.reset()
        counts['target_calls'] += 1 + len(word)
        return [engine.step(action) for action in word]
    try:
        _, _, probes, _, info = _acquire(case.public, 'fixed', 8, query, counts, None, None,
                                         escalate=True, probe_safety='model_safe')
    finally:
        engine.close()
    envelope = CandidateSpace(Machine.from_dict(case.public['reference']), Contract(), temporal=True)
    assert probes
    evidence = []
    for probe in probes:
        ids = envelope.survivors(evidence, case.public['anchors'])
        assert probe['safety']['model_class'] == 'temporal'
        assert probe['safety']['candidate_count'] == len(ids)
        assert all(envelope.contract.hazard not in envelope.semantic(i, probe['word']) for i in ids)
        evidence.append(probe)
    assert info['calibration']['safety_model_class'] == 'temporal'


def _public_result(**config):
    public = make_case('latch', 17).public
    cfg = asdict(RunConfig(**config))
    space = CandidateSpace(Machine.from_dict(public['reference']), Contract.from_dict(public['contract']))
    ids = space.survivors([])
    return {'schema': 'crosswire-result-v1', 'configuration': cfg,
            'reference': public['reference'], 'contract': public['contract'],
            'target_id': 'test', 'anchors': {}, 'probes': [],
            'candidates': [space.adapters[i].to_dict() for i in ids],
            'decision': space.plan(ids)}, space


def test_checker_refuses_unsafe_calibration_even_after_evidence_refutes_hazardous_maps():
    result, space = _public_result(probe_safety='model_safe')
    probe = {'word': [0], 'outputs': [0], 'complete': True}
    ids = space.survivors([probe])
    result.update(probes=[probe], candidates=[space.adapters[i].to_dict() for i in ids],
                  decision=space.plan(ids))
    checked = check_result(result)
    assert checked['valid'] is False
    assert 'calibration' in checked['reason'].lower()


@pytest.mark.parametrize('bad', [2, True, '2', 'nan', float('nan'), -0.1, 1])
def test_risk_certificate_rejects_forged_or_invalid_tolerance(bad):
    result, _ = _public_result(admission='risk_controlled')
    result['decision'].update(admitted=True, status='RISK_CONTROLLED_ADMISSIBLE', word=[0],
                              risk_metrics={'hazard_risk': 0.0, 'goal_rate': 1.0, 'tolerance': bad})
    assert check_result(result)['valid'] is False


def test_risk_certificate_binds_tolerance_to_config_and_checks_declared_rates():
    result = run(RunConfig(family='latch', seed=42, budget=16, admission='risk_controlled',
                          risk_tolerance=0.2))
    assert result['decision']['risk_metrics']['tolerance'] == 0.2
    assert check_result(result)['valid'] is True
    for field, value in [('tolerance', 0.3), ('hazard_risk', 0.5), ('goal_rate', 0.0)]:
        forged = deepcopy(result)
        forged['decision']['risk_metrics'][field] = value
        assert check_result(forged)['valid'] is False


def test_valid_positive_tolerance_is_certified_as_candidate_fractions():
    result, space = _public_result(admission='risk_controlled', risk_tolerance=0.9)
    result['decision'] = space.plan(space.survivors([]), 'risk_controlled', risk_tolerance=0.9)
    assert result['decision']['admitted'] is True
    checked = check_result(result)
    assert checked['valid'] is True and checked['kind'] == 'risk_controlled'
    assert 'not a calibrated' in checked['reason']


def test_checker_does_not_silently_relax_configured_fraction_threshold():
    result, _ = _public_result(admission='risk_controlled', risk_tolerance=2 / 3 - 1e-10)
    machine = Machine('fraction boundary', (((0, 1), (0, 2), (0, 0)),))
    contract = Contract(horizon=1)
    space = CandidateSpace(machine, contract)
    result.update(reference=machine.to_dict(), contract=contract.to_dict(),
                  candidates=[a.to_dict() for a in space.adapters])
    result['decision'].update(admitted=True, status='RISK_CONTROLLED_ADMISSIBLE', word=[0],
                              risk_metrics={'hazard_risk': 1 / 3, 'goal_rate': 1 / 3,
                                            'tolerance': 2 / 3 - 1e-10})
    assert check_result(result)['valid'] is False


def test_unresolved_risk_certificate_rejects_fabricated_selected_plan_rates():
    result, space = _public_result(admission='risk_controlled')
    result['decision'] = space.plan(space.survivors([]), 'risk_controlled')
    assert result['decision']['admitted'] is False
    assert check_result(result)['valid'] is True
    result['decision']['risk_metrics']['hazard_risk'] = 0.0
    assert check_result(result)['valid'] is False


def test_safe_certificate_checks_unexecuted_suffix_of_interrupted_attempt():
    public = make_case('routing', 17, anchors=True).public
    space = CandidateSpace(Machine.from_dict(public['reference']), Contract())
    anchors = public['anchors']
    # All first three actions are safe; one interpretation hazards at the fourth.
    probe = {'word': [0, 0, 0, 0], 'outputs': [0], 'complete': False}
    ids = space.survivors([{'word': [0], 'outputs': [0], 'complete': True}], anchors)
    result = {'schema': 'crosswire-result-v1', 'configuration': asdict(RunConfig(probe_safety='model_safe')),
              'reference': public['reference'], 'contract': public['contract'], 'anchors': anchors,
              'target_id': 'test', 'probes': [probe], 'candidates': [space.adapters[i].to_dict() for i in ids],
              'decision': {'status': 'INTERFACE_ERROR', 'admitted': False, 'word': None, 'candidate_count': len(ids)}}
    assert check_result(result)['valid'] is False


def test_safe_run_and_exact_receipt_replay():
    from crosswire.receipts import pack, replay
    result = run(RunConfig(family='latch', budget=16, probe_safety='model_safe'))
    assert result['metrics']['target_calls'] == 0
    assert result['decision']['calibration']['stop_reason'] == 'NO_ELIGIBLE_SAFE_PROBE'
    assert result['audit']['calibration_hazardous_probes'] == 0
    assert result['evidence_certificate']['calibration_safety']['safe'] is True
    assert replay(pack(result))['valid'] is True


def test_new_conditions_flow_through_study_and_prevent_false_pairing():
    configs = study_configs({'families': ['routing'], 'probe_safety': 'model_safe',
                             'risk_tolerance': 0.2, 'admissions': ['risk_controlled']})
    assert all(c.probe_safety == 'model_safe' and c.risk_tolerance == 0.2 for c in configs)
    def row(policy, safety='unrestricted', tolerance=0.0):
        cfg = asdict(RunConfig(policy=policy, probe_safety=safety, risk_tolerance=tolerance,
                              admission='risk_controlled'))
        return {'configuration': cfg, 'parent_instance_id': 'p1',
                'audit': {'contract_satisfied': policy == 'entropy'}}
    assert paired_comparisons([row('entropy'), row('fixed', 'model_safe')]) == []
    assert paired_comparisons([row('entropy'), row('fixed', tolerance=0.2)]) == []
    pairs = paired_comparisons([row('entropy'), row('fixed')])
    assert len(pairs) == 1
    assert pairs[0]['contrast'] == 'entropy - fixed'
    assert pairs[0]['mean_delta'] == 1.0
