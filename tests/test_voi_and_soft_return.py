import pytest
from crosswire.core import CandidateSpace, FactoredCandidateSpace, Machine, Contract
from crosswire.fixtures import make_case
from crosswire.shield import RuntimeShield, execute_deployment, synthesize_safe_return
from crosswire.study import RunConfig, run, POLICIES, RECOVERY_STRATEGIES
from crosswire.certificates import check_result


def test_policies_and_recovery_strategies_registered():
    assert "voi" in POLICIES
    assert "stabilize" in RECOVERY_STRATEGIES
    assert "soft_return" in RECOVERY_STRATEGIES


def test_information_profile_includes_expected_readiness():
    case = make_case("latch", 17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]),
                           Contract.from_dict(case.public["contract"]))
    all_ids = tuple(range(len(space.adapters)))
    prof = space.information_profile(all_ids, (0,))
    assert "expected_task_readiness" in prof
    assert 0.0 <= prof["expected_task_readiness"] <= 1.0
    assert prof["candidate_count"] == len(all_ids)


def test_choose_probe_voi_policy_selects_informative_probe():
    case = make_case("latch", 17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]),
                           Contract.from_dict(case.public["contract"]))
    all_ids = tuple(range(len(space.adapters)))
    probe = space.choose_probe(all_ids, "voi", 3, seen=set())
    assert probe is not None
    assert isinstance(probe, tuple)
    assert 1 <= len(probe) <= 3


def test_choose_probe_voi_model_safe():
    case = make_case("routing", 17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]),
                           Contract.from_dict(case.public["contract"]))
    all_ids = tuple(range(len(space.adapters)))
    probe = space.choose_probe(all_ids, "voi", 3, seen=set(), safe_only=True)
    assert probe is not None
    assert space.probe_is_safe(all_ids, probe)


def test_choose_probe_voi_on_factored_space():
    case = make_case("routing", 17)
    space = FactoredCandidateSpace(Machine.from_dict(case.public["reference"]),
                                   Contract.from_dict(case.public["contract"]))
    all_ids = tuple(range(space.total_adapters))
    probe = space.choose_probe(all_ids, "voi", 3, seen=set(), safe_only=True)
    assert probe is not None
    assert space.probe_is_safe(all_ids, probe)


def test_end_to_end_run_with_voi_policy():
    cfg = RunConfig(family="latch", seed=17, budget=8, policy="voi", admission="robust")
    res = run(cfg)
    assert res["schema"] == "crosswire-result-v1"
    assert res["configuration"]["policy"] == "voi"
    assert res["evidence_certificate"]["valid"] is True
    if res["decision"]["admitted"]:
        assert res["audit"]["contract_satisfied"] is True


def test_end_to_end_run_with_voi_policy_model_safe():
    cfg = RunConfig(family="latch", seed=17, budget=8, policy="voi",
                    admission="robust", probe_safety="model_safe")
    res = run(cfg)
    assert res["evidence_certificate"]["valid"] is True
    assert res["decision"]["calibration"]["mode"] == "model_safe"
    assert res["audit"]["calibration_hazardous_probes"] == 0


def test_runtime_shield_soft_return_recovery():
    case = make_case("latch", 17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]),
                           Contract.from_dict(case.public["contract"]))
    survivors = space.survivors([])

    class MockTarget:
        def __init__(self):
            self.history = []
            self.state = 0
            self.counts = {"step_attempts": 0, "reset_attempts": 0, "target_calls": 0}

        def reset(self):
            self.state = 0
            self.counts["reset_attempts"] += 1
            self.counts["target_calls"] += 1

        def step(self, action):
            self.counts["step_attempts"] += 1
            self.counts["target_calls"] += 1
            self.history.append(action)
            if self.state == 0 and action == 0:
                self.state = 1
                return 0
            if self.state == 1 and action == 1:
                self.state = 2
                return 1
            self.state = 0
            return 3

    target = MockTarget()
    shield = RuntimeShield(space, survivors, space.contract, mode="recovery",
                           recovery_strategy="soft_return")
    rec_out = shield.recover(target)
    rec_record = shield.recovery_record()

    assert rec_record["requested"] is True
    assert rec_record["strategy"] == "soft_return"
    assert rec_record["certified"] is True
    assert rec_record["succeeded"] is True
    assert rec_record["return_to_initial"] is True
    assert rec_record["reason"] == "already_at_initial"


def test_runtime_shield_soft_return_from_armed_state():
    case = make_case("latch", 17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]),
                           Contract.from_dict(case.public["contract"]))
    id_adapter = next(a.id for a in space.adapters if a.input_map == (0, 1, 2) and a.output_map == (0, 1, 2, 3))
    survivors = (id_adapter,)

    class MockTarget:
        def __init__(self):
            self.state = 1
            self.counts = {"step_attempts": 0, "reset_attempts": 0, "target_calls": 0}

        def reset(self):
            self.state = 0

        def step(self, action):
            self.counts["step_attempts"] += 1
            self.counts["target_calls"] += 1
            return 3

    target = MockTarget()
    shield = RuntimeShield(space, survivors, space.contract, mode="recovery",
                           recovery_strategy="soft_return")
    shield.history_words = [0]
    shield.history_outputs = [0]

    rec_out = shield.recover(target)
    record = shield.recovery_record()
    assert record["requested"] is True
    assert record["strategy"] == "soft_return"
    assert record["attempted"] is True
    assert record["succeeded"] is True
    assert isinstance(record["actions"], list)


def test_run_config_recovery_strategy_validation():
    with pytest.raises(ValueError, match="Unknown recovery strategy"):
        RunConfig(recovery_strategy="invalid_mode").check()

    cfg = RunConfig(recovery_strategy="soft_return")
    assert cfg.recovery_strategy == "soft_return"


def test_model_diagnostics_tracks_surprisal_bits():
    cfg = RunConfig(family="latch", seed=17, budget=8, policy="entropy")
    res = run(cfg)
    cert = res["evidence_certificate"]
    diag = cert.get("model_diagnostics", {})
    assert "classes" in diag
    for cls_name, cls_diag in diag["classes"].items():
        assert "cumulative_surprisal_bits" in cls_diag
        assert "mean_symbol_surprisal_bits" in cls_diag
        assert cls_diag["cumulative_surprisal_bits"] >= 0.0
        assert cls_diag["mean_symbol_surprisal_bits"] >= 0.0
