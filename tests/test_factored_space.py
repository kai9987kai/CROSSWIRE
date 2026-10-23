import time
import pytest
from crosswire.core import CandidateSpace, FactoredCandidateSpace, Contract, Machine
from crosswire.fixtures import make_case


def test_factored_space_decomposition_and_composition_bijection():
    case = make_case('latch', seed=42)
    m = Machine.from_dict(case.public['reference'])
    c = Contract.from_dict(case.public['contract'])

    space = FactoredCandidateSpace(m, c, temporal=True)
    assert space.total_adapters == 720
    assert space.static_count == 144
    assert space.temporal_count == 576

    for aid in range(space.total_adapters):
        i_idx, o_idx, delay, init_o = space.decompose_id(aid)
        recomposed = space.compose_id(i_idx, o_idx, delay=delay, init_output=init_o)
        assert recomposed == aid


def test_factored_space_exact_parity_on_latch():
    case = make_case('latch', seed=42)
    m = Machine.from_dict(case.public['reference'])
    c = Contract.from_dict(case.public['contract'])

    cs_flat = CandidateSpace(m, c, temporal=True)
    cs_fact = FactoredCandidateSpace(m, c, temporal=True)

    assert len(cs_flat.adapters) == len(cs_fact.adapters) == 720

    # Test traces and predictions across sampled adapter IDs
    test_word = (0, 1, 0, 2)
    for aid in (0, 1, 5, 143, 144, 250, 500, 719):
        assert cs_flat.adapters[aid].input_map == cs_fact.adapter(aid).input_map
        assert cs_flat.adapters[aid].output_map == cs_fact.adapter(aid).output_map
        assert cs_flat.semantic(aid, test_word) == cs_fact.semantic(aid, test_word)
        assert cs_flat.predict(aid, test_word) == cs_fact.predict(aid, test_word)
        assert cs_flat.safe_words(aid) == cs_fact.safe_words(aid)

    # Use ground-truth predictions from adapter 0 so adapter 0 is guaranteed to survive
    target_aid = 0
    pred1 = cs_flat.predict(target_aid, (0, 1))
    pred2 = cs_flat.predict(target_aid, (0, 0, 1))
    evidence = [
        {'word': [0, 1], 'outputs': list(pred1), 'complete': True},
        {'word': [0, 0, 1], 'outputs': list(pred2), 'complete': True}
    ]
    target_ad = cs_flat.adapters[target_aid]
    anchors = {target_ad.output_map[0]: 0, target_ad.output_map[1]: 1}

    surv_flat = cs_flat.survivors(evidence, anchors)
    surv_fact = cs_fact.survivors(evidence, anchors)
    assert surv_flat == surv_fact
    assert target_aid in surv_fact
    assert len(surv_fact) > 0

    # Test plan exact match
    plan_flat = cs_flat.plan(surv_flat, 'robust')
    plan_fact = cs_fact.plan(surv_fact, 'robust')
    assert plan_flat == plan_fact


def test_factored_space_exact_parity_on_routing():
    case = make_case('routing', seed=17)
    m = Machine.from_dict(case.public['reference'])
    c = Contract.from_dict(case.public['contract'])

    cs_flat = CandidateSpace(m, c, temporal=False)
    cs_fact = FactoredCandidateSpace(m, c, temporal=False)

    assert len(cs_flat.adapters) == len(cs_fact.adapters) == 144

    target_aid = 5
    pred = cs_flat.predict(target_aid, (0, 1, 2))
    evidence = [{'word': [0, 1, 2], 'outputs': list(pred), 'complete': True}]
    anchors = {cs_flat.adapters[target_aid].output_map[0]: 0}

    surv_flat = cs_flat.survivors(evidence, anchors)
    surv_fact = cs_fact.survivors(evidence, anchors)
    assert surv_flat == surv_fact
    assert target_aid in surv_fact


def test_factored_space_lazy_adapters_proxy():
    case = make_case('latch', seed=42)
    m = Machine.from_dict(case.public['reference'])
    c = Contract.from_dict(case.public['contract'])
    space = FactoredCandidateSpace(m, c, temporal=True)

    adapters = space.adapters
    assert len(adapters) == 720
    a0 = adapters[0]
    assert a0.id == 0
    assert hasattr(a0, 'input_map')
    assert hasattr(a0, 'output_map')

    # Slicing
    first_three = adapters[0:3]
    assert len(first_three) == 3
    assert [a.id for a in first_three] == [0, 1, 2]

    # Iteration
    count = 0
    for a in adapters:
        count += 1
        if count >= 10:
            break
    assert count == 10


def test_factored_space_factor_summary():
    case = make_case('latch', seed=42)
    m = Machine.from_dict(case.public['reference'])
    c = Contract.from_dict(case.public['contract'])
    space = FactoredCandidateSpace(m, c, temporal=True)

    summary = space.factor_summary()
    assert summary['total_models'] == 720
    assert summary['static_models'] == 144
    assert summary['temporal_models'] == 576
    assert summary['input_permutations'] == 6
    assert summary['output_permutations'] == 24
    assert summary['active_input_factors'] == 6
    assert summary['active_output_factors'] == 24
    assert summary['compression_ratio'] == 24.0

    # Pruned summary
    evidence = [{'word': [0, 1], 'outputs': [0, 1], 'complete': True}]
    anchors = {0: 0, 1: 1}
    survivors = space.survivors(evidence, anchors)
    pruned_summary = space.factor_summary(survivors)
    assert pruned_summary['survivors_count'] == len(survivors)
    assert pruned_summary['active_input_factors'] <= 6
    assert pruned_summary['active_output_factors'] <= 24


def test_factored_space_scaling_17280_models():
    # 4-input 5-output machine produces 24 * 120 = 2,880 static + 2,880 * 5 = 14,400 temporal
    # Total = 17,280 models!
    m_large = Machine("scale_17k", (
        ((1,0),(2,1),(3,2),(0,3)),
        ((2,1),(3,2),(0,3),(1,0)),
        ((3,2),(0,3),(1,0),(2,1)),
        ((0,3),(1,0),(2,1),(3,2))
    ), inputs=4, outputs=5, initial=0)
    c_large = Contract(goal=1, hazard=2, horizon=4)

    t0 = time.perf_counter()
    cs_large = FactoredCandidateSpace(m_large, c_large, temporal=True)
    t1 = time.perf_counter()
    assert t1 - t0 < 0.05  # Instant instantiation with O(N_I + N_O) memory

    summary = cs_large.factor_summary()
    assert summary['total_models'] == 17280
    assert summary['static_models'] == 2880
    assert summary['temporal_models'] == 14400
    assert summary['input_permutations'] == 24
    assert summary['output_permutations'] == 120
    assert summary['compression_ratio'] == 120.0

    # Pruning on 17,280 space
    evidence = [{'word': [0, 1, 2], 'outputs': [0, 1, 2], 'complete': True}]
    anchors = {0: 0, 1: 1, 2: 2}

    t2 = time.perf_counter()
    survivors = cs_large.survivors(evidence, anchors)
    t3 = time.perf_counter()

    # Pruning must be lightning-fast (< 0.1s for 17,280 models)
    assert t3 - t2 < 0.1
    assert len(survivors) > 0
    assert all(0 <= s < 17280 for s in survivors)

    # All survivors strictly satisfy anchors and evidence
    for s in survivors:
        pred = cs_large.predict(s, (0, 1, 2))
        assert pred == (0, 1, 2)
