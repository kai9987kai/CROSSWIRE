"""Tests for Priority 5: Adaptive within-query branching calibration."""
import pytest
from crosswire.core import CandidateSpace, Machine, Contract
from crosswire.fixtures import make_case, make_engine
from crosswire.study import RunConfig, run, _acquire, POLICIES
from crosswire.receipts import pack, replay
from crosswire.certificates import check_result


def test_policies_contains_branching():
    assert "branching" in POLICIES


def test_choose_branching_step_entropy():
    case = make_case("latch", seed=17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]), Contract.from_dict(case.public["contract"]))
    ids = space.survivors([], {})
    
    # Selecting the first step from root: should pick an informative action (score > 0)
    action = space.choose_branching_step(ids, (), safe_only=False)
    assert action in (0, 1, 2)
    
    # When ids <= 1: should return None
    assert space.choose_branching_step(list(ids)[:1], (), safe_only=False) is None
    assert space.choose_branching_step([], (), safe_only=False) is None


def test_choose_branching_step_model_safe_filters_hazard():
    case = make_case("latch", seed=17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]), Contract.from_dict(case.public["contract"]))
    ids = space.survivors([], {})
    
    # Safe step must not trigger contract hazard under any surviving model
    safe_action = space.choose_branching_step(ids, (), safe_only=True)
    if safe_action is not None:
        assert space.probe_is_safe(ids, (safe_action,))


def test_acquire_branching_early_termination():
    case = make_case("neutral", seed=17)
    counts = {"target_calls": 0}
    engine = make_engine(case.private)

    def query(word):
        counts["target_calls"] += len(word) + 1
        engine.reset()
        return [engine.step(x) for x in word]

    space, survivors, probes, error, info = _acquire(
        case.public, "branching", budget=16, query=query, counts=counts,
        cancel=None, progress=None, step=engine.step, reset=engine.reset
    )
    # Neutral is immediately contract-ready, so it should admit with minimal or 0 probes
    assert space.plan(survivors, "robust")["admitted"]
    assert error is None


def test_branching_full_run_and_replay_unrestricted():
    config = RunConfig(
        family="latch",
        seed=17,
        budget=16,
        policy="branching",
        admission="robust",
        execution_mode="shielded",
        probe_safety="unrestricted"
    )
    result = run(config)
    assert result["decision"]["admitted"] is True
    assert result["audit"]["contract_satisfied"] is True
    assert result["audit"]["hazard"] is False

    # Check evidence certificate
    cert_check = check_result(result)
    assert cert_check["valid"] is True
    assert cert_check["kind"] == "admission"

    # Verify exact scientific replay
    receipt = pack(result)
    replay_check = replay(receipt)
    assert replay_check["valid"] is True
    assert replay_check["scientific_hash"] == result["scientific_hash"]


def test_branching_model_safe_with_anchors_and_replay():
    config = RunConfig(
        family="routing",
        seed=17,
        budget=16,
        policy="branching",
        admission="robust",
        execution_mode="shielded",
        probe_safety="model_safe",
        anchors=True
    )
    result = run(config)
    assert result["decision"]["admitted"] is True
    assert result["audit"]["contract_satisfied"] is True
    assert result["audit"]["hazard"] is False

    # Check evidence certificate
    cert_check = check_result(result)
    assert cert_check["valid"] is True
    assert cert_check["kind"] == "admission"

    # Verify exact scientific replay
    receipt = pack(result)
    replay_check = replay(receipt)
    assert replay_check["valid"] is True
    assert replay_check["scientific_hash"] == result["scientific_hash"]


def test_branching_model_safe_abstains_when_all_actions_hazardous():
    config = RunConfig(
        family="latch",
        seed=17,
        budget=16,
        policy="branching",
        admission="robust",
        execution_mode="shielded",
        probe_safety="model_safe",
        anchors=False
    )
    result = run(config)
    assert result["decision"]["admitted"] is False
    assert result["decision"]["status"] == "UNRESOLVED"
    assert len(result["probes"]) == 0


def test_branching_vs_fixed_efficiency():
    config_branching = RunConfig(
        family="handshake",
        seed=42,
        budget=16,
        policy="branching",
        admission="robust",
        execution_mode="shielded"
    )
    res_branching = run(config_branching)

    config_fixed = RunConfig(
        family="handshake",
        seed=42,
        budget=16,
        policy="fixed",
        admission="robust",
        execution_mode="shielded"
    )
    res_fixed = run(config_fixed)

    assert res_branching["decision"]["admitted"] is True
    assert res_branching["audit"]["contract_satisfied"] is True
    assert res_branching["metrics"]["target_calls"] <= res_fixed["metrics"]["target_calls"]


def test_branching_temporal_escalation():
    config = RunConfig(
        family="delay",
        seed=42,
        budget=16,
        policy="branching",
        admission="robust",
        execution_mode="shielded",
        escalate=True
    )
    res = run(config)
    assert res["decision"]["admitted"] is True
    assert res["audit"]["contract_satisfied"] is True
    assert res["decision"]["escalation"]["escalated"] is True


def test_branching_temporal_explicit():
    config = RunConfig(
        family="delay",
        seed=17,
        budget=16,
        policy="branching",
        admission="robust",
        execution_mode="shielded",
        temporal=True
    )
    res = run(config)
    assert res["decision"]["admitted"] is True
    assert res["audit"]["contract_satisfied"] is True
