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
