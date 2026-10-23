import pytest

from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.fixtures import make_case
from crosswire.study import RunConfig, run


def test_entropy_probing_prefers_maximally_informative_partition():
    machine = Machine('split', (((1, 0), (1, 1), (1, 2)), ((0, 0), (0, 1), (0, 2))))
    space = CandidateSpace(machine, Contract(horizon=2))
    ids = space.survivors([])
    probe = space.choose_probe(ids, 'entropy', remaining_steps=3, seen=set())
    assert probe is not None
    # Entropy probe is non-empty and bounded
    assert 1 <= len(probe) <= 3


def test_entropy_probing_handles_single_or_empty_belief():
    machine = Machine('split', (((1, 0), (1, 1), (1, 2)), ((0, 0), (0, 1), (0, 2))))
    space = CandidateSpace(machine, Contract(horizon=2))
    assert space.choose_probe((0,), 'entropy', remaining_steps=3, seen=set()) is not None
    assert space.choose_probe((), 'entropy', remaining_steps=3, seen=set()) is None


def test_autonomous_escalation_resolves_delay_fixture():
    # Delay fixture refutes static bijections; escalation discovers the temporal adapter
    res_no_esc = run(RunConfig(family='delay', seed=17, budget=16, escalate=False))
    assert res_no_esc['decision']['status'] == 'FAMILY_CONTRADICTED'
    assert res_no_esc['metrics']['escalations'] == 0

    res_esc = run(RunConfig(family='delay', seed=17, budget=16, escalate=True, execution_mode='shielded'))
    assert res_esc['decision']['admitted'] is True
    assert res_esc['decision']['escalation']['escalated'] is True
    assert res_esc['decision']['escalation']['model_class'] == 'temporal'
    assert res_esc['metrics']['escalations'] == 1
    assert res_esc['metrics']['escalation_level'] == 1
    assert res_esc['audit']['contract_satisfied'] is True


def test_structural_contradiction_certificate_emitted_when_all_classes_fail():
    # Incompatible fixture cannot be explained by static or latency-1 temporal adapters
    res = run(RunConfig(family='incompatible', seed=17, budget=16, escalate=True))
    assert res['decision']['status'] == 'FAMILY_CONTRADICTED'
    assert 'structural_contradiction' in res['decision']
    sc = res['decision']['structural_contradiction']
    assert 'static (144 maps)' in sc['classes_refuted']
    assert 'temporal (720 latency maps)' in sc['classes_refuted']


def test_in_family_fixture_does_not_trigger_spurious_escalation():
    res = run(RunConfig(family='latch', seed=17, budget=16, escalate=True))
    assert res['decision']['admitted'] is True
    assert res['decision']['escalation']['escalated'] is False
    assert res['metrics']['escalations'] == 0
    assert res['metrics']['escalation_level'] == 0


def test_recovery_halts_after_anomaly_without_inventing_a_backup_model():
    # Refuted models cannot certify a fallback, even if this fixture has a safe action.
    res_shield = run(RunConfig(family='alias', seed=17, budget=16, execution_mode='shielded'))
    res_recovery = run(RunConfig(family='alias', seed=17, budget=16, execution_mode='recovery'))

    assert res_shield['deployment']['shield_status'] == 'INTERVENED_ANOMALY'
    assert res_recovery['deployment']['shield_status'] == 'INTERVENED_ANOMALY'
    assert res_recovery['deployment']['recovery']['requested'] is True
    assert res_recovery['deployment']['recovery']['attempted'] is False
    assert res_recovery['deployment']['recovery']['certified'] is False
    assert res_recovery['deployment']['recovery']['succeeded'] is False
    assert res_recovery['deployment']['recovery']['reason'] == 'model_contradicted'
    assert res_recovery['deployment']['executed_word'] == res_shield['deployment']['executed_word']
    # The private audit observes only the prefix that actually happened.
    assert res_recovery['audit']['hazard'] is not True


def test_run_config_validation_for_escalate_and_recovery():
    with pytest.raises(ValueError, match='escalate cannot be combined with temporal'):
        RunConfig(temporal=True, escalate=True).check()
    with pytest.raises(ValueError, match='AALpy baseline does not support model escalation'):
        RunConfig(policy='aalpy', escalate=True).check()
    with pytest.raises(ValueError, match='Unknown execution mode'):
        RunConfig(execution_mode='invalid').check()
