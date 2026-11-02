"""Whole-runtime backend and checked experiment planning contracts."""
from copy import deepcopy
from dataclasses import asdict

import pytest

from crosswire.certificates import check_result
from crosswire.reliability import reliability_summary
from crosswire.study import RunConfig, paired_comparisons, run, run_study, study_configs, summarize
from crosswire.receipts import pack, replay


def test_backend_study_dimension_and_conditions_are_explicit():
    configs = study_configs({'families': ['latch'], 'seeds': [17], 'budgets': [0],
                             'policies': ['lookahead'], 'candidate_backends': ['flat', 'factored']})
    assert {cfg.candidate_backend for cfg in configs} == {'flat', 'factored'}
    with pytest.raises(ValueError, match='candidate_backend'):
        RunConfig.from_dict({'candidate_backend': 'pretend'})
    with pytest.raises(ValueError, match='Duplicate'):
        study_configs({'candidate_backends': ['factored', 'factored']})


@pytest.mark.parametrize('configuration', [
    {'family': 'latch', 'policy': 'task', 'budget': 8},
    {'family': 'routing', 'policy': 'branching', 'budget': 8, 'probe_safety': 'model_safe'},
    {'family': 'delay', 'policy': 'entropy', 'budget': 8, 'temporal': True},
    {'family': 'delay', 'policy': 'fixed', 'budget': 8, 'escalate': True, 'probe_safety': 'model_safe'},
    {'family': 'routing', 'budget': 0, 'admission': 'adaptive', 'execution_mode': 'shielded'},
    {'family': 'symmetric', 'budget': 0, 'admission': 'risk_controlled', 'risk_tolerance': 0.25},
    {'family': 'latch', 'policy': 'lookahead', 'budget': 4},
])
def test_backends_preserve_observed_experiments_and_admission(configuration):
    flat = run(RunConfig(**configuration, candidate_backend='flat'))
    factored = run(RunConfig(**configuration, candidate_backend='factored'))
    for result, name in ((flat, 'flat'), (factored, 'factored')):
        assert result['backend']['backend'] == name
        assert result['configuration']['candidate_backend'] == name
        assert check_result(result)['valid'] is True
    for field in ('probes', 'decision', 'candidates', 'deployment'):
        assert flat[field] == factored[field], field
    for field in ('contract_satisfied', 'hazard', 'calibration_hazardous_probes'):
        assert flat['audit'][field] == factored['audit'][field]


def test_lookahead_records_independently_checked_pre_observation_trees_and_rejects_tampering():
    result = run(RunConfig(family='latch', policy='lookahead', budget=4, candidate_backend='factored'))
    assert result['probes']
    planned = result['probes'][0]['planning']
    assert planned['certificate']['valid'] is True
    assert planned['certificate']['worst_case_calls'] <= planned['remaining_calls'] == 4
    assert planned['tree']['word'] == result['probes'][0]['word']
    assert replay(pack(result))['valid'] is True
    forged = deepcopy(result)
    forged['probes'][0]['planning']['certificate']['ready_models'] += 1
    assert check_result(forged)['valid'] is False
    forged = deepcopy(result)
    forged['probes'][0]['planning']['remaining_calls'] = 512
    assert check_result(forged)['valid'] is False
    forged = deepcopy(result)
    forged['configuration']['candidate_backend'] = 'pretend'
    assert check_result(forged)['valid'] is False


def test_guarded_lookahead_abstains_without_a_safe_first_action():
    result = run(RunConfig(family='latch', policy='lookahead', budget=4,
                           candidate_backend='factored', probe_safety='model_safe'))
    assert result['probes'] == []
    assert result['metrics']['target_calls'] == 0
    assert not result['decision']['admitted']


def test_study_stratifies_backends_and_replays_exactly():
    result = run_study({'families': ['latch'], 'seeds': [17], 'budgets': [2],
                        'policies': ['lookahead'], 'candidate_backends': ['flat', 'factored']})
    assert len(result['summary']) == len(result['reliability']) == 2
    assert {row['candidate_backend'] for row in result['summary']} == {'flat', 'factored'}
    assert replay(pack(result))['valid'] is True


def test_backend_conditions_never_match_across_policy_comparisons():
    def row(backend, policy):
        return {'configuration': asdict(RunConfig(candidate_backend=backend, policy=policy)),
                'parent_instance_id': 'same', 'audit': {'contract_satisfied': True}}
    assert paired_comparisons([row('flat', 'task'), row('factored', 'entropy')]) == []
