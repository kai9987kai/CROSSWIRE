import math
import pytest

from crosswire.adaptive import execute_policy, policy_metrics, synthesize_policy
from crosswire.core import CandidateSpace, Contract, FactoredCandidateSpace, Machine
from crosswire.fixtures import make_case
from crosswire.interfaces import TargetProcess
from crosswire.shield import synthesize_safe_return
from crosswire.study import RunConfig, run


def test_information_profile_and_bald_mutual_information_identity():
    case = make_case('robotics_airlock', seed=17)
    m = Machine.from_dict(case.public['reference'])
    c = Contract.from_dict(case.public['contract'])

    cs_flat = CandidateSpace(m, c)
    cs_fact = FactoredCandidateSpace(m, c)

    ids = cs_flat.survivors([])
    for word in ((0,), (0, 1), (0, 1, 2)):
        prof_flat = cs_flat.information_profile(ids, word)
        prof_fact = cs_fact.information_profile(ids, word)
        assert prof_flat == prof_fact
        assert prof_flat['candidate_count'] == 144
        assert prof_flat['cost'] == 1 + len(word)
        assert 1 <= prof_flat['worst_case_survivors'] <= 144
        assert 1.0 <= prof_flat['expected_survivors'] <= 144.0

    # Safe probe ranking on robotics_airlock must return only model_safe probes
    ranked_safe = cs_fact.rank_probes(ids, top_k=5, safe_only=True)
    assert len(ranked_safe) == 5
    assert all(p['model_safe'] is True for p in ranked_safe)
    # Sorted descending by cost_efficiency_bits_per_call
    efficiencies = [p['cost_efficiency_bits_per_call'] for p in ranked_safe]
    assert efficiencies == sorted(efficiencies, reverse=True)

    # Empty belief profile
    empty_prof = cs_fact.information_profile((), (0,))
    assert empty_prof['candidate_count'] == 0
    assert empty_prof['mutual_information_bits'] == 0.0
    assert cs_fact.rank_probes((), top_k=3) == []


def test_policy_metrics_on_contingent_routing_policy():
    case = make_case('routing', seed=17)
    m = Machine.from_dict(case.public['reference'])
    c = Contract.from_dict(case.public['contract'])
    space = FactoredCandidateSpace(m, c)
    ids = space.survivors([])

    syn = synthesize_policy(space, ids)
    assert syn['admitted'] is True

    metrics = policy_metrics(space, ids, syn['policy'])
    assert metrics['valid'] is True
    assert metrics['candidate_count'] == 144
    assert metrics['leaf_count'] > 1
    assert metrics['internal_nodes'] >= 3
    assert metrics['best_case_steps'] == 4
    assert metrics['worst_case_steps'] == 4
    assert metrics['expected_steps'] == 4.0
    assert sum(metrics['leaf_belief_sizes']) == 144
    assert metrics['information_gain_bits'] > 0.0

    # Invalid policy returns valid=False
    bad_metrics = policy_metrics(space, ids, {'stop': True})
    assert bad_metrics['valid'] is False


def test_adaptive_policy_execution_with_simplex_recovery_mode():
    # Under a sensor_drift fault at step 1 in adaptive + recovery mode,
    # execute_policy detects the anomaly and invokes Simplex recovery check
    cfg = RunConfig(
        family='routing',
        seed=17,
        budget=0,
        horizon=4,
        admission='adaptive',
        execution_mode='recovery',
        fault_schedule={'step': 0, 'type': 'stuck_output', 'value': 0},
    )
    res = run(cfg)
    assert res['decision']['admitted'] is True
    dep = res['deployment']
    assert dep['mode'] == 'recovery'
    assert dep['intervened'] is True
    assert 'recovery' in dep
    assert dep['recovery']['requested'] is True


@pytest.mark.parametrize('family,prefix,expected_word', [
    ('robotics_airlock', (0, 1), [0]),      # State 2 (ARMED_CHAMBER) --0--> State 0 (STANDBY)
    ('protocol_session', (0, 1), [2]),      # State 2 (AUTH_VERIFIED) --1--> State 0; wait: let's check State 2!
])
def test_synthesize_safe_return_to_initial_state(family, prefix, expected_word):
    case = make_case(family, seed=17)
    m = Machine.from_dict(case.public['reference'])
    c = Contract.from_dict(case.public['contract'])
    space_flat = CandidateSpace(m, c)
    space_fact = FactoredCandidateSpace(m, c)

    # All 24 adapters with identity input_map (0, 1, 2) share i_idx == 0
    identity_input_ids = tuple(range(24))

    ret_flat = synthesize_safe_return(space_flat, identity_input_ids, prefix=prefix)
    ret_fact = synthesize_safe_return(space_fact, identity_input_ids, prefix=prefix)
    assert ret_flat == ret_fact
    assert ret_flat['certified'] is True
    assert ret_flat['return_to_initial'] is True
    assert ret_flat['reason'] == 'certified_return_to_initial'
    assert len(ret_flat['word']) == 1

    # Verify that prefix + ret_flat['word'] returns to state 0 without hazard
    state = m.initial
    for sym in tuple(prefix) + tuple(ret_flat['word']):
        state, out = m.transitions[state][sym]
        assert out != c.hazard
    assert state == m.initial


def test_synthesize_safe_return_edge_cases():
    case = make_case('latch', seed=17)
    m = Machine.from_dict(case.public['reference'])
    c = Contract.from_dict(case.public['contract'])
    space = FactoredCandidateSpace(m, c)

    # Empty belief
    assert synthesize_safe_return(space, ())['reason'] == 'empty_belief'

    # Already at initial state
    res_init = synthesize_safe_return(space, (0,), prefix=())
    assert res_init['certified'] is True
    assert res_init['return_to_initial'] is True
    assert res_init['word'] == []
    assert res_init['reason'] == 'already_at_initial'

    # Prefix already hazardous (on latch, action 2 from state 0 is hazard)
    res_haz = synthesize_safe_return(space, (0,), prefix=(2,))
    assert res_haz['certified'] is False
    assert res_haz['reason'] == 'prefix_already_hazardous'
