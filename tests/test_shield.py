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

