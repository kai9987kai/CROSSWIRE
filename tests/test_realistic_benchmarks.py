import itertools
import pytest

from crosswire.certificates import check_result
from crosswire.fixtures import catalog, evaluate_word, make_case, oracle_plan, target_machine
from crosswire.study import RunConfig, run


@pytest.mark.parametrize('family,state_count,goal_word,goal_events,hazard_word,hazard_events', [
    ('robotics_airlock', 5, (0, 1, 2), (0, 0, 1), (0, 1, 1), (0, 0, 2)),
    ('protocol_session', 6, (0, 1, 0, 2), (0, 0, 3, 1), (0, 1, 2), (0, 0, 2)),
])
def test_realistic_benchmarks_exhaustive_table_procedural_parity_and_semantics(
    family, state_count, goal_word, goal_events, hazard_word, hazard_events
):
    entry = next(row for row in catalog() if row['id'] == family)
    assert entry['scope'] == 'in_family'

    cases = [make_case(family, seed=29, implementation=impl, anchors=True) for impl in ('table', 'procedural')]
    assert cases[0].public['parent_instance_id'] == cases[1].public['parent_instance_id']

    models = [target_machine(c.private) for c in cases]
    assert len(models[0].transitions) == state_count
    assert models[0].transitions == models[1].transitions

    for length in range(1, 5):
        for word in itertools.product(range(3), repeat=length):
            t_res, p_res = [evaluate_word(c.private, word) for c in cases]
            assert t_res == p_res
            assert tuple(t_res['outputs']) == models[0].trace(word)

    inverse = {val: key for key, val in enumerate(cases[0].private['input_map'])}
    mapped_goal = [inverse[a] for a in goal_word]
    res_goal = evaluate_word(cases[0].private, mapped_goal)
    assert res_goal['semantic_events'] == list(goal_events)
    assert res_goal['contract_satisfied'] is True and res_goal['hazard'] is False

    mapped_hazard = [inverse[a] for a in hazard_word]
    res_hazard = evaluate_word(cases[0].private, mapped_hazard)
    assert res_hazard['semantic_events'] == list(hazard_events)
    assert res_hazard['hazard'] is True and res_hazard['contract_satisfied'] is False


def test_protocol_session_requires_four_step_horizon_beyond_shallow_probes():
    case = make_case('protocol_session', seed=17)
    assert oracle_plan(case.private, horizon=3) is None
    plan4 = oracle_plan(case.private, horizon=4)
    assert plan4 is not None and len(plan4) == 4
    assert evaluate_word(case.private, plan4)['contract_satisfied'] is True


@pytest.mark.parametrize('family', ['robotics_airlock', 'protocol_session'])
def test_model_safe_calibration_achieves_zero_hazard_goal_without_anchors(family):
    cfg = RunConfig(
        family=family,
        seed=17,
        budget=28,
        horizon=4,
        policy='task',
        admission='robust',
        probe_safety='model_safe',
        anchors=False,
        execution_mode='shielded',
    )
    result = run(cfg)
    assert check_result(result)['valid'] is True
    assert result['decision']['admitted'] is True
    assert result['audit']['calibration_hazardous_probes'] == 0
    assert result['audit']['hazard'] is False
    assert result['audit']['goal_success'] is True
    assert result['audit']['contract_satisfied'] is True


@pytest.mark.parametrize('family', ['robotics_airlock', 'protocol_session'])
def test_branching_calibration_and_change_point_shield_on_realistic_benchmarks(family):
    cfg = RunConfig(
        family=family,
        seed=42,
        budget=24,
        horizon=4,
        policy='branching',
        admission='robust',
        probe_safety='model_safe',
        anchors=True,
        execution_mode='shielded',
        fault_schedule={'step': 1, 'type': 'sensor_drift', 'phase': 'deployment'},
    )
    result = run(cfg)
    assert check_result(result)['valid'] is True
    assert result['decision']['admitted'] is True
    assert result['audit']['calibration_hazardous_probes'] == 0
    cp = result['audit']['change_point']
    assert cp['scheduled'] is True
    assert cp['type'] == 'sensor_drift'
    assert cp['detected'] is True
    assert cp['detection_latency'] is not None and cp['detection_latency'] >= 0
