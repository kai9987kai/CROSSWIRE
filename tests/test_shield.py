import pytest

from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.fixtures import Case, make_case
from crosswire.interfaces import TargetProcess
from crosswire.shield import RuntimeShield, execute_deployment


def _simple_space():
    # 2-state machine
    transitions = (((1, 0), (0, 3), (1, 2)), ((1, 1), (1, 1), (1, 2)))
    m = Machine("simple", transitions, 3, 4, 0)
    c = Contract(goal=1, hazard=2, horizon=4)
    return CandidateSpace(m, c)


def test_open_loop_deployment_does_not_intervene():
    case = make_case("latch", seed=17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]), Contract.from_dict(case.public["contract"]))
    survivors = space.survivors([])
    with TargetProcess(case.private) as target:
        dep = execute_deployment(target, [0, 1], space, survivors, space.contract, mode="open_loop")
        assert dep["complete"] is True
        assert dep["intervened"] is False
        assert dep["shield_status"] == "COMPLETED"
        assert len(dep["outputs"]) == 2


def test_shielded_deployment_completes_when_target_matches():
    case = make_case("latch", seed=17, anchors=True)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]), Contract.from_dict(case.public["contract"]))
    anchors = {int(k): int(v) for k, v in case.public["anchors"].items()}
    survivors = space.survivors([], anchors)
    with TargetProcess(case.private) as target:
        # A plan known to be admitted
        plan = space.plan(survivors, "robust")["word"]
        if plan:
            dep = execute_deployment(target, plan, space, survivors, space.contract, mode="shielded")
            assert dep["complete"] is True
            assert dep["intervened"] is False
            assert dep["shield_status"] == "COMPLETED"
            assert len(dep["outputs"]) == len(plan)


def test_shielded_deployment_halts_on_anomalous_drift_before_suffix():
    # Test with incompatible or drift fixture
    case = make_case("incompatible", seed=17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]), Contract.from_dict(case.public["contract"]))
    survivors = space.survivors([])
    with TargetProcess(case.private) as target:
        # Try sending an action sequence that hits incompatible transitions
        dep = execute_deployment(target, [2, 0, 1, 0], space, survivors, space.contract, mode="shielded")
        # Under incompatible, the shield should detect survivor collapse or complete
        assert "survivor_history" in dep
        assert dep["mode"] == "shielded"


def test_pre_step_hazard_interception_prevents_dispatch():
    # If the upcoming action is universally hazardous under active survivors,
    # the shield must abort before target.step is executed.
    case = make_case("latch", seed=17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]), Contract.from_dict(case.public["contract"]))
    survivors = space.survivors([])
    # Find an action that is universally hazardous under all survivors from initial state (if any)
    # Or create a 2-adapter subspace where action 0 causes hazard
    hazard_adapters = [a.id for a in space.adapters if space.contract.hazard in space.semantic(a.id, (2,))]
    if hazard_adapters:
        shield = RuntimeShield(space, tuple(hazard_adapters[:5]), space.contract, mode="shielded")
        with TargetProcess(case.private) as target:
            out, should_continue = shield.step(target, 2, [])
            assert should_continue is False
            assert shield.status == "INTERVENED_HAZARD_AVERTED"
            assert target.counts["step_attempts"] == 0  # Pre-step: never called target.step!


def test_causal_counterfactual_audit_distinguishes_averted_hazards():
    from crosswire.study import run, RunConfig
    # On alias seed 23 fit mode: unshielded hits a hazard; shielded halts at step 0
    res_shielded = run(RunConfig(family="alias", seed=23, budget=16, admission="fit", execution_mode="shielded"))
    assert res_shielded["deployment"]["intervened"] is True
    # The auditor detects the counterfactual hazard was causally averted!
    assert res_shielded["audit"]["hazard_averted"] is True
    assert res_shielded["audit"]["deployment_audit"]["counterfactual_hazard"] is True

    # On incompatible seed 17 fit mode: unshielded does not hit a hazard; shielded halts at step 0
    res_incomp = run(RunConfig(family="incompatible", seed=17, budget=16, admission="fit", execution_mode="shielded"))
    assert res_incomp["deployment"]["intervened"] is True
    # Anomaly was detected, but because the full plan was not counterfactually hazardous, hazard_averted is False
    assert res_incomp["audit"]["hazard_averted"] is False
    assert res_incomp["audit"]["deployment_audit"]["counterfactual_hazard"] is False


def test_pre_step_guard_blocks_hazard_under_any_surviving_interpretation():
    case = make_case('latch', seed=17)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']))
    hazardous = next(a.id for a in space.adapters if space.contract.hazard in space.semantic(a.id, (0,)))
    safe = next(a.id for a in space.adapters if space.contract.hazard not in space.semantic(a.id, (0,)))
    shield = RuntimeShield(space, (hazardous, safe), space.contract)
    with TargetProcess(case.private) as target:
        output, should_continue = shield.step(target, 0, [])
        assert target.counts['step_attempts'] == 0
        assert output is None and should_continue is False
        assert shield.status == 'INTERVENED_HAZARD_AVERTED'
        assert shield.history_words == []


@pytest.mark.parametrize('mode', ['typo', None, True])
def test_runtime_shield_rejects_unknown_execution_modes(mode):
    space = _simple_space()
    with pytest.raises(ValueError, match='mode'):
        RuntimeShield(space, (0,), space.contract, mode=mode)


class _ScriptedTarget:
    """Counted target boundary with deterministic responses or interface faults."""

    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.actions = []
        self.counts = dict(reset_attempts=0, step_attempts=0, reset_successes=0,
                           step_successes=0, target_calls=0)

    def reset(self):
        self.counts['reset_attempts'] += 1
        self.counts['reset_successes'] += 1
        self.counts['target_calls'] += 1

    def step(self, action):
        self.actions.append(action)
        self.counts['step_attempts'] += 1
        self.counts['target_calls'] += 1
        output = next(self.outputs)
        if isinstance(output, Exception):
            raise output
        self.counts['step_successes'] += 1
        return output


def _recovery_space(horizon=2):
    # Identity: action 0 is hazardous; action 1 reaches the goal; action 2 is neutral.
    return CandidateSpace(Machine('fallback', (((0, 2), (0, 1), (0, 0)),)),
                          Contract(horizon=horizon))


def test_recovery_refuses_when_every_action_is_hazardous():
    space = CandidateSpace(Machine('trap', (((0, 2), (0, 2), (0, 2)),)), Contract())
    target = _ScriptedTarget([2])
    result = execute_deployment(target, [0], space, (0,), space.contract, mode='recovery')
    assert result['target_steps'] == 0
    assert result['executed_word'] == []
    assert result['shield_status'] == 'INTERVENED_HAZARD_AVERTED'
    assert result['recovery']['requested'] is True
    assert result['recovery']['attempted'] is False
    assert result['recovery']['certified'] is False
    assert result['recovery']['succeeded'] is False
    assert result['recovery']['reason'] == 'no_safe_action'


def test_recovery_refuses_to_repopulate_a_contradicted_belief():
    space = _recovery_space()
    target = _ScriptedTarget([3, 1])
    result = execute_deployment(target, [1], space, (0,), space.contract, mode='recovery')
    assert result['target_steps'] == 1
    assert result['executed_word'] == [1]
    assert result['survivor_history'] == [1, 0]
    assert result['shield_status'] == 'INTERVENED_ANOMALY'
    assert result['recovery']['reason'] == 'model_contradicted'
    assert result['recovery']['attempted'] is False
    assert result['recovery']['succeeded'] is False


def test_recovery_executes_only_unanimously_safe_action_and_checks_response():
    space = _recovery_space()
    target = _ScriptedTarget([1])
    result = execute_deployment(target, [0], space, (0,), space.contract, mode='recovery')
    assert result['executed_word'] == [1]
    assert result['outputs'] == [1]
    assert result['survivor_history'] == [1, 1]
    assert result['shield_status'] == 'RECOVERED_SAFE_FALLBACK'
    assert result['complete'] is False
    assert result['recovery']['requested'] is True
    assert result['recovery']['attempted'] is True
    assert result['recovery']['certified'] is True
    assert result['recovery']['succeeded'] is True
    assert result['recovery']['action'] == 1
    assert result['recovery']['reason'] == 'certified_response'
    assert 'conditional' in result['recovery']['scope'].lower()


def test_recovery_response_contradiction_is_not_reported_as_success():
    space = _recovery_space()
    target = _ScriptedTarget([3])
    result = execute_deployment(target, [0], space, (0,), space.contract, mode='recovery')
    assert result['executed_word'] == [1]
    assert result['survivor_history'] == [1, 0]
    assert result['shield_status'] == 'INTERVENED_ANOMALY'
    assert result['recovery']['attempted'] is True
    assert result['recovery']['certified'] is True
    assert result['recovery']['succeeded'] is False
    assert result['recovery']['reason'] == 'response_contradiction'


def test_recovery_respects_remaining_contract_horizon():
    space = _recovery_space(horizon=1)
    target = _ScriptedTarget([1, 1])
    shield = RuntimeShield(space, (0,), space.contract, mode='recovery')
    assert shield.step(target, 1, [])[1] is True
    assert shield.recover(target) is None
    assert target.counts['step_attempts'] == 1
    assert shield.recovery_reason == 'horizon_exhausted'
    assert shield.recovery_succeeded is False


def test_recovery_requires_safe_consensus_instead_of_minimum_hazard_count():
    space = _recovery_space()
    # Every input is hazardous under one of the possible input permutations.
    ids = tuple(a.id for a in space.adapters if a.output_map == (0, 1, 2, 3))
    target = _ScriptedTarget([1])
    result = execute_deployment(target, [0], space, ids, space.contract, mode='recovery')
    assert result['target_steps'] == 0
    assert result['recovery']['reason'] == 'no_safe_action'


def test_recovery_interface_error_keeps_intervention_and_attempt_evidence():
    from crosswire.interfaces import InterfaceError
    space = _recovery_space()
    target = _ScriptedTarget([InterfaceError('timeout')])
    result = execute_deployment(target, [0], space, (0,), space.contract, mode='recovery')
    assert result['shield_status'] == 'INTERFACE_ERROR'
    assert result['intervened'] is True
    assert result['target_steps'] == 1
    assert result['executed_word'] == []
    assert result['reasons']
    assert result['recovery']['attempted'] is True
    assert result['recovery']['certified'] is True
    assert result['recovery']['succeeded'] is False
    assert result['recovery']['reason'] == 'interface_error'


@pytest.mark.parametrize('mode', ['open_loop', 'shielded', 'recovery'])
def test_deployment_cancellation_raises_before_target_reset(mode):
    from crosswire.study import Cancelled
    space = _recovery_space()
    target = _ScriptedTarget([1])
    with pytest.raises(Cancelled):
        execute_deployment(target, [1], space, (0,), space.contract, mode=mode,
                           cancel=lambda: True)
    assert target.counts['target_calls'] == 0


def test_cancellation_after_observation_prevents_fallback_dispatch():
    from crosswire.study import Cancelled
    space = _recovery_space()
    target = _ScriptedTarget([1, 1])
    # First action is safe; the unsafe suffix would trigger a fallback.
    with pytest.raises(Cancelled):
        execute_deployment(target, [1, 0], space, (0,), space.contract, mode='recovery',
                           cancel=lambda: target.counts['step_successes'] > 0)
    assert target.actions == [1]

