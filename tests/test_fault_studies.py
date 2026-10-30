"""Controlled faults remain separate from nominal evidence throughout analysis."""
from copy import deepcopy
from dataclasses import asdict

import pytest

from crosswire.fixtures import evaluate_calibration, evaluate_deployment, make_case, target_machine
from crosswire.reliability import reliability_summary
from crosswire.study import RunConfig, paired_comparisons, study_configs, summarize


@pytest.mark.parametrize('schedule', [
    {'step': 0, 'type': 'sensor_drift', 'phase': 'typo'},
    {'step': 0, 'type': 'sensor_drift', 'extra': True},
    {'step': 0, 'type': 'sensor_drift', 'value': 0},
    *[{'step': 0, 'type': 'stuck_output', 'value': value}
      for value in (True, -1, 4, 1.5, '0')],
])
def test_fault_schedule_rejects_invalid_phase_keys_and_sensor_symbols(schedule):
    with pytest.raises(ValueError, match='fault_schedule'):
        RunConfig.from_dict({'fault_schedule': schedule})


def test_fault_grid_normalizes_defaults_and_rejects_effective_duplicates():
    spec = {'families': ['latch'], 'seeds': [17], 'budgets': [0],
            'policies': ['fixed'], 'fault_schedules': [None, {'step': 2, 'type': 'stuck_output'}]}
    configs = study_configs(spec)
    assert len(configs) == 2
    assert configs[0].fault_schedule is None
    assert configs[1].fault_schedule == {'step': 2, 'type': 'stuck_output', 'phase': 'deployment', 'value': 0}
    with pytest.raises(ValueError, match='Duplicate'):
        study_configs({**spec, 'fault_schedules': [
            {'step': 2, 'type': 'stuck_output'},
            {'step': 2, 'type': 'stuck_output', 'phase': 'deployment', 'value': 0}]})
    with pytest.raises(ValueError, match='512'):
        study_configs({**spec, 'seeds': list(range(64)), 'budgets': list(range(9))})


def _row(policy='task', schedule=None):
    cfg = asdict(RunConfig(family='generated_protocol', instance_seed=2, policy=policy,
                          fault_schedule=schedule))
    return {'configuration': cfg, 'parent_instance_id': 'same-dynamics',
            'decision': {'admitted': True, 'status': 'TASK_ADMISSIBLE'},
            'audit': {'contract_satisfied': True, 'oracle_feasible': True,
                      'hazard': False, 'calibration_hazardous_probes': 0},
            'metrics': {'target_calls': 0, 'target_steps': 0, 'resets': 0},
            'deployment': {'target_calls': 0}}


def test_fault_conditions_never_pool_or_match_across_schedules():
    schedules = [None, {'step': 1, 'type': 'sensor_drift'},
                 {'step': 2, 'type': 'sensor_drift'},
                 {'step': 1, 'type': 'semantic_swap'}]
    rows = [_row(schedule=schedule) for schedule in schedules]
    before = deepcopy(rows)
    assert len(summarize(rows)) == len(schedules)
    assert len(reliability_summary(rows)) == len(schedules)
    assert all('fault_schedule' in summary for summary in summarize(rows))
    assert paired_comparisons([_row(), _row('fixed', schedules[1])]) == []
    paired = paired_comparisons([_row(schedule=schedules[1]), _row('fixed', schedules[1])])
    assert len(paired) == 1
    assert paired[0]['fault_schedule']['step'] == 1
    assert rows == before


@pytest.mark.parametrize('phase', ['calibration', 'deployment', 'always'])
@pytest.mark.parametrize('kind', ['sensor_drift', 'actuator_swap', 'delay_spike', 'stuck_output', 'semantic_swap'])
@pytest.mark.parametrize('implementation', ['table', 'procedural'])
@pytest.mark.parametrize('family', ['latch', 'delay', 'repeat'])
def test_exported_fault_model_matches_actual_deployment_before_and_after_onset(phase, kind, implementation, family):
    case = make_case(family, seed=17, implementation=implementation,
                     fault_schedule={'step': 1, 'type': kind, 'phase': phase})
    model = target_machine(case.private)
    assert model is not None
    for word in ((0,), (0, 1), (0, 1, 2, 0, 1), (2, 2, 1, 0)):
        assert model.trace(word) == tuple(evaluate_deployment(case.private, [], word)['outputs'])


@pytest.mark.parametrize('family', ['latch', 'alias', 'delay', 'repeat'])
@pytest.mark.parametrize('kind', ['sensor_drift', 'delay_spike', 'stuck_output'])
def test_scheduled_sensor_faults_compose_with_existing_sensor_mechanisms(family, kind):
    word = (0, 1, 2, 0, 1)
    nominal = make_case(family, seed=17)
    faulted = make_case(family, seed=17, fault_schedule={'step': 0, 'type': kind, 'value': 3}
                        if kind == 'stuck_output' else {'step': 0, 'type': kind})
    baseline = evaluate_deployment(nominal.private, [], word)['outputs']
    output_map = nominal.private['output_map']
    if kind == 'sensor_drift':
        expected = [output_map[(output_map.index(raw) + 1) % 4] for raw in baseline]
    elif kind == 'delay_spike':
        expected = [output_map[0], *baseline[:-1]]
    else:
        expected = [output_map[3]] * len(word)
    assert evaluate_deployment(faulted.private, [], word)['outputs'] == expected


@pytest.mark.parametrize('family', ['latch', 'semantic_corruption', 'bypass', 'drift'])
@pytest.mark.parametrize('phase', ['calibration', 'deployment', 'always'])
def test_scheduled_semantic_fault_composes_with_existing_semantic_mechanisms(family, phase):
    nominal = make_case(family, seed=17)
    inverse = {meaning: raw for raw, meaning in enumerate(nominal.private['input_map'])}
    word = [inverse[0], inverse[1]] * 6  # Cross the drift family's experiment-level onset too.
    faulted = make_case(family, seed=17, fault_schedule={'step': 1, 'type': 'semantic_swap', 'phase': phase})
    baseline = evaluate_deployment(nominal.private, [], word)
    actual = evaluate_deployment(faulted.private, [], word)
    expected = [({1: 2, 2: 1}.get(event, event) if index >= 1 and phase != 'calibration' else event)
                for index, event in enumerate(baseline['semantic_events'])]
    assert actual['semantic_events'] == expected
    assert actual['outputs'] == baseline['outputs']


def test_very_distant_fault_onset_withholds_exact_model_instead_of_unbounded_expansion():
    case = make_case('latch', fault_schedule={'step': 10**9, 'type': 'sensor_drift'})
    assert target_machine(case.private) is None


@pytest.mark.parametrize('phase,expected', [('calibration', 1), ('deployment', 0), ('always', 1)])
def test_private_calibration_hazard_count_uses_actual_probe_phase(phase, expected):
    from crosswire.audit import evaluate
    from crosswire.core import CandidateSpace, Contract, Machine
    case = make_case('latch', horizon=1, fault_schedule={'step': 0, 'type': 'semantic_swap', 'phase': phase})
    inverse = {meaning: raw for raw, meaning in enumerate(case.private['input_map'])}
    word = [inverse[0], inverse[1]]
    probe = {'word': word, 'outputs': evaluate_calibration(case.private, [], word)['outputs'], 'complete': True}
    space = CandidateSpace(Machine.from_dict(case.public['reference']), Contract.from_dict(case.public['contract']))
    audit = evaluate(case, space, space.survivors([]), {'admitted': False, 'word': None}, [probe],
                     {'complete': False, 'outputs': []})
    assert audit['calibration_hazardous_probes'] == expected


def test_fault_study_preserves_negative_control_and_replays_exactly():
    from crosswire.certificates import check_result
    from crosswire.receipts import pack, replay
    from crosswire.study import run_study
    result = run_study({'families': ['latch'], 'seeds': [42], 'budgets': [16],
                        'policies': ['task'], 'admissions': ['robust'], 'execution_mode': 'shielded',
                        'fault_schedules': [None, {'step': 2, 'type': 'sensor_drift'},
                                            {'step': 1, 'type': 'semantic_swap'}]})
    assert len(result['rows']) == len(result['summary']) == len(result['reliability']) == 3
    assert all(check_result(row)['valid'] for row in result['rows'])
    nominal, sensor, semantic = result['rows']
    assert nominal['audit']['contract_satisfied'] is True
    assert sensor['deployment']['change_point']['detected'] is True
    assert semantic['deployment']['change_point']['detected'] is False
    assert semantic['audit']['hazard'] is True
    assert replay(pack(result))['valid'] is True
