import pytest
from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.fixtures import make_case
from crosswire.interfaces import TargetProcess
from crosswire.shield import RuntimeShield, execute_deployment
from crosswire.study import RunConfig, run


def test_replan_mode_accepted_by_runtime_shield():
    case = make_case('latch', seed=42)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']))
    survivors = tuple(a.id for a in space.adapters)
    shield = RuntimeShield(space, survivors, space.contract, mode='replan')
    assert shield.mode == 'replan'
    assert shield.replanned is False
    assert shield.replan_events == []


def test_replan_finds_safe_alternative_suffix():
    case = make_case('latch', seed=42)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']))
    # Target process
    target = TargetProcess(case.private)
    try:
        survivors = tuple(a.id for a in space.adapters)
        shield = RuntimeShield(space, survivors, space.contract, mode='replan')
        # Check that _find_safe_suffix returns a valid non-empty suffix or None
        suffix = shield._find_safe_suffix((), remaining_horizon=4)
        if suffix is not None:
            assert isinstance(suffix, tuple)
            assert 1 <= len(suffix) <= 4
            assert all(space.contract.accepts(space.semantic(aid, suffix)) for aid in shield.active_survivors)
    finally:
        target.close()


def test_replan_execution_completes_goal_on_latch():
    config = RunConfig(family='latch', seed=42, budget=16, execution_mode='replan', admission='robust')
    result = run(config)
    assert result['schema'] == 'crosswire-result-v1'
    assert result['configuration']['execution_mode'] == 'replan'
    dep = result['deployment']
    assert dep['mode'] == 'replan'
    assert 'replanned' in dep
    assert 'replan_events' in dep
    assert result['audit']['contract_satisfied'] is True
    assert result['audit']['hazard'] is False


def test_replan_on_misspecified_stress_averts_hazard():
    # In alias or delay without temporal, replan should intervene and avert hazard
    config = RunConfig(family='delay', seed=42, budget=16, execution_mode='replan', admission='robust')
    result = run(config)
    assert result['schema'] == 'crosswire-result-v1'
    dep = result['deployment']
    assert dep['mode'] == 'replan'
    # Should never execute a hazard
    assert result['audit']['hazard'] is not True


def test_replan_actively_rewrites_risky_plan_to_safe_detour():
    transitions = (
        ((1, 0), (0, 0), (0, 2)),  # state 0: 0->s1, 1->s0, 2->hazard(2)
        ((1, 0), (1, 1), (0, 2)),  # state 1: 0->s1, 1->goal(1), 2->hazard(2)
    )
    m = Machine("replan_demo", transitions, 3, 4, 0)
    c = Contract(goal=1, hazard=2, horizon=4)
    space = CandidateSpace(m, c)

    class MockTarget:
        def __init__(self):
            self.state = 0
            self.counts = {'step_attempts': 0, 'reset_attempts': 0, 'target_calls': 0}
        def reset(self):
            self.state = 0
            self.counts['reset_attempts'] += 1
            self.counts['target_calls'] += 1
        def step(self, action):
            self.counts['step_attempts'] += 1
            self.counts['target_calls'] += 1
            self.state, out = transitions[self.state][action]
            return out

    identity_id = next(a.id for a in space.adapters if a.input_map == (0, 1, 2) and a.output_map == (0, 1, 2, 3))
    target = MockTarget()
    # Initial plan is [0, 2] where 2 is hazardous at step 2. Replan should switch to [1] and reach the goal.
    dep = execute_deployment(target, [0, 2], space, (identity_id,), c, mode="replan")
    assert dep['replanned'] is True
    assert dep['replan_count'] >= 1
    assert dep['executed_word'] == [0, 1]
    assert dep['complete'] is True
    assert dep['shield_status'] == "REPLANNED_ONLINE_SAFE"
