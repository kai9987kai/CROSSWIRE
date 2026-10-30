"""Finite certification regressions independent of source-bound run receipts."""
import pytest

from crosswire.adaptive import execute_policy, policy_metrics
from crosswire.core import CandidateSpace, Contract, FactoredCandidateSpace, Machine
from crosswire.shield import execute_deployment, synthesize_safe_return


@pytest.mark.parametrize('space_type', [CandidateSpace, FactoredCandidateSpace])
def test_policy_metrics_distinguish_same_actions_with_different_observations(space_type):
    machine = Machine('observed_goal', (((0, 1),),), inputs=1, outputs=3)
    space = space_type(machine, Contract(horizon=1))
    # Both adapters reach the semantic goal, but their raw observations differ.
    policy = {'action': 0, 'branches': {'0': {'stop': True}, '1': {'stop': True}}}

    metrics = policy_metrics(space, (0, 2), policy)

    assert metrics['valid'] is True
    assert metrics['leaf_count'] == 2
    assert metrics['leaf_belief_sizes'] == [1, 1]
    assert metrics['information_gain_bits'] == 1.0
    assert metrics['expected_steps'] == 1.0


def return_space(horizon):
    machine = Machine('return_cycle', (((1, 0),), ((2, 0),), ((0, 0),)),
                      inputs=1, outputs=3)
    return CandidateSpace(machine, Contract(horizon=horizon))


def test_safe_return_override_cannot_extend_exhausted_horizon():
    result = synthesize_safe_return(return_space(1), (0,), prefix=(0,), max_length=2)

    assert result['certified'] is False
    assert result['word'] is None
    assert result['reason'] == 'horizon_exhausted'


def test_safe_return_caps_override_and_selects_in_horizon_holding_step():
    result = synthesize_safe_return(return_space(2), (0,), prefix=(0,), max_length=10**9)

    assert result['certified'] is True
    assert result['return_to_initial'] is False
    assert result['word'] == [0]
    assert result['reason'] == 'certified_safe_hold'


def test_safe_return_rejects_prefix_longer_than_contract_even_if_at_initial():
    with pytest.raises(ValueError, match='prefix.*horizon'):
        synthesize_safe_return(return_space(1), (0,), prefix=(0, 0, 0))


@pytest.mark.parametrize('max_length', [True, False, 1.0, '1'])
def test_safe_return_rejects_noninteger_search_bounds_before_initial_return(max_length):
    with pytest.raises(TypeError, match='max_length'):
        synthesize_safe_return(return_space(3), (0,), max_length=max_length)


def test_safe_return_rejects_negative_search_bound_before_initial_return():
    with pytest.raises(ValueError, match='max_length'):
        synthesize_safe_return(return_space(3), (0,), max_length=-1)


def test_safe_return_allows_empty_return_at_exact_horizon():
    result = synthesize_safe_return(return_space(3), (0,), prefix=(0, 0, 0), max_length=0)

    assert result['certified'] is True
    assert result['return_to_initial'] is True
    assert result['word'] == []


@pytest.mark.parametrize('space_type', [CandidateSpace, FactoredCandidateSpace])
def test_contract_plan_accepts_extra_neutral_output_before_goal(space_type):
    machine = Machine('fifth_output', (((1, 4),), ((1, 1),)), inputs=1, outputs=5)
    space = space_type(machine, Contract(horizon=2))

    decision = space.plan((0,))

    assert decision['admitted'] is True
    assert decision['word'] == [0, 0]


@pytest.mark.parametrize('symbols,accepted', [([4, 1], True), ([4], False), ([4, 2, 1], False)])
def test_contract_retains_goal_and_hazard_semantics_with_extra_symbols(symbols, accepted):
    assert Contract().accepts(symbols) is accepted


@pytest.mark.parametrize('symbol', [True, -1, 1.0, '4'])
def test_contract_still_rejects_invalid_semantic_symbols(symbol):
    with pytest.raises((TypeError, ValueError)):
        Contract().accepts([symbol, 1])


@pytest.mark.parametrize('executor', ['fixed', 'adaptive'])
@pytest.mark.parametrize('phase,detected', [('calibration', False), ('deployment', True), ('always', True)])
def test_deployment_mismatch_only_marks_faults_applicable_to_deployment(executor, phase, detected):
    # This deterministic target deliberately contradicts the certified model.
    class MismatchingTarget:
        def __init__(self):
            self.counts = {'reset_attempts': 0, 'step_attempts': 0, 'target_calls': 0}

        def reset(self):
            self.counts['reset_attempts'] += 1
            self.counts['target_calls'] += 1

        def step(self, action):
            self.counts['step_attempts'] += 1
            self.counts['target_calls'] += 1
            return 0

    machine = Machine('observed_goal', (((0, 1),),), inputs=1, outputs=3)
    contract = Contract(horizon=1)
    space = CandidateSpace(machine, contract)
    schedule = {'step': 0, 'type': 'sensor_drift', 'phase': phase}
    if executor == 'fixed':
        deployment = execute_deployment(MismatchingTarget(), [0], space, (0,), contract,
                                        mode='shielded', fault_schedule=schedule)
    else:
        policy = {'action': 0, 'branches': {'1': {'stop': True}}}
        deployment = execute_policy(MismatchingTarget(), policy, space, (0,), fault_schedule=schedule)

    assert deployment['intervened'] is True
    assert deployment['change_point']['scheduled'] is True
    assert deployment['change_point']['detected'] is detected
    assert deployment['change_point']['detection_step'] == (0 if detected else None)
    assert deployment['change_point']['detection_latency'] == (0 if detected else None)
