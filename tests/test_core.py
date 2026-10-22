from itertools import combinations
import random

import pytest

from crosswire.core import Adapter, CandidateSpace, Contract, Machine, compare_adapter, words


def source():
    return Machine('latch', (((1, 0), (0, 2), (0, 3)), ((1, 0), (1, 1), (0, 3))))


def aid(space, inputs=(0, 1, 2), outputs=(0, 1, 2, 3)):
    return next(a.id for a in space.adapters if a.input_map == inputs and a.output_map == outputs)


def test_exact_144_fixed_bijections_and_direction():
    space = CandidateSpace(source(), Contract())
    assert len(space.adapters) == 144
    assert len({(a.input_map, a.output_map) for a in space.adapters}) == 144
    a = aid(space, (1, 0, 2), (3, 2, 0, 1))
    assert space.semantic(a, (1, 0)) == (0, 1)
    assert space.predict(a, (1, 0)) == (3, 2)
    assert space.predict(a, (0, 1)) == (0, 3)


def test_prefix_hazard_never_erased_by_terminal_goal():
    assert not Contract().accepts((2, 1))
    assert not Contract().accepts(())
    assert Contract().accepts((0, 3, 1))
    machine = Machine('hazard-first', (((1, 2), (0, 0), (0, 0)), ((1, 1), (1, 1), (1, 1))))
    space = CandidateSpace(machine, Contract(horizon=2))
    assert not space.safe_words(aid(space))


def test_fitting_retains_true_mapping_and_ignores_incomplete_entries():
    space = CandidateSpace(source(), Contract())
    true = aid(space, (2, 0, 1), (2, 0, 3, 1))
    transcript = [{'word': w, 'outputs': space.predict(true, w), 'complete': True} for w in words(3, 3)]
    survivors = space.survivors(transcript)
    assert true in survivors
    assert space.losses(transcript)[true] == 0
    assert space.survivors([{'word': [0], 'outputs': [99], 'complete': False}]) == tuple(range(144))
    assert space.survivors(transcript, {2: 0}) == tuple(i for i in survivors if space.adapters[i].output_map[0] == 2)


def test_task_equivalent_mapping_ambiguity_allows_robust_but_not_unique():
    machine = Machine('neutral', (((0, 1), (0, 0), (0, 0)),))
    space = CandidateSpace(machine, Contract())
    ids = (aid(space), aid(space, outputs=(0, 1, 3, 2)))
    assert space.ambiguity(ids) == {'map_count': 2, 'observational_classes': 1, 'contract_classes': 1}
    assert space.plan(ids)['status'] == 'TASK_ADMISSIBLE'
    assert space.plan(ids)['word'] == [0]
    assert not space.plan(ids, 'unique')['admitted']
    assert space.plan(ids[:1])['status'] == 'IDENTIFIED'


def test_symmetric_raw_equivalence_can_hide_conflicting_semantics():
    machine = Machine('symmetric', (((0, 1), (0, 2), (0, 0)),))
    space = CandidateSpace(machine, Contract())
    ids = (aid(space), aid(space, inputs=(1, 0, 2), outputs=(0, 2, 1, 3)))
    assert space.ambiguity(ids) == {'map_count': 2, 'observational_classes': 1, 'contract_classes': 2}
    assert not space.plan(ids)['admitted']
    assert space.choose_probe(ids, 'task', 100, set()) is None


def test_empty_family_is_never_vacuously_admitted_and_forced_modes_explicit():
    space = CandidateSpace(source(), Contract())
    for mode in ('robust', 'one_best', 'unique', 'abstain'):
        result = space.plan((), mode)
        assert result['status'] == 'FAMILY_CONTRADICTED'
        assert result['word'] is None and not result['admitted']
    assert space.plan((), 'identity')['word'] == [0, 1]
    assert space.plan((), 'fit', transcripts=[])['admitted']
    with pytest.raises(ValueError):
        space.plan((0,), 'unknown')


def test_probe_cost_nonrepeatability_random_reproducibility_and_scores():
    space = CandidateSpace(source(), Contract(horizon=2))
    ids = (0, 1, 24, 25, 48)
    seen = {(0,), (1,)}
    assert space.choose_probe(ids, 'fixed', 0, seen) is None
    assert space.choose_probe(ids, 'fixed', 1, seen) == (2,)
    assert len(space.choose_probe(ids, 'fixed', 2, {(0,), (1,), (2,)})) == 2
    state = random.getstate()
    assert space.choose_probe(ids, 'random', 4, seen, seed=22) == space.choose_probe(ids, 'random', 4, seen, seed=22)
    assert state == random.getstate()
    pool = [w for w in words(3, 3) if len(w) <= 4 and w not in seen]
    assert space.choose_probe(ids, 'random', 4, seen, seed=22) == random.Random(22).choice(sorted(pool))
    for policy in ('task', 'disagreement'):
        scores = {}
        for w in pool:
            total = 0
            for a, b in combinations(ids, 2):
                sa, sb = space.safe_words(a), space.safe_words(b)
                weight = 1 if policy == 'disagreement' else len(sa ^ sb) / max(1, len(sa | sb))
                if space.predict(a, w) != space.predict(b, w):
                    total += weight
            scores[w] = total / (1 + len(w))
        best = min(pool, key=lambda w: (-scores[w], len(w), w))
        expected = best if scores[best] > 0 else None
        assert space.choose_probe(ids, policy, 4, seen) == expected


def test_prediction_cache_counts_only_actual_new_source_steps():
    space = CandidateSpace(source(), Contract())
    assert space.work == {'source_steps': 0, 'candidate_expansions': 0, 'pair_checks': 0}
    space.predict(0, (0, 1))
    assert space.work['source_steps'] == 2
    before = dict(space.work)
    space.predict(0, (0, 1))
    space.semantic(0, (0, 1))
    assert space.work == before
    space.predict(1, (0, 1))  # same input map, distinct output map
    assert space.work['source_steps'] == 2
    space.predict(0, (0, 1, 2))
    assert space.work['source_steps'] == 3


def test_pair_checks_count_executed_predictions_not_zero_weight_pairs():
    machine = Machine('neutral', (((0, 1), (0, 0), (0, 0)),))
    space = CandidateSpace(machine, Contract())
    equivalent = (aid(space), aid(space, outputs=(0, 1, 3, 2)))
    assert space.choose_probe(equivalent, 'task', 3, set()) is None
    assert space.work['pair_checks'] == 0
    ids = equivalent + (aid(space, inputs=(1, 0, 2)),)
    before = space.work['pair_checks']
    assert space.choose_probe(ids, 'task', 3, set()) is not None
    assert space.work['pair_checks'] - before == 2 * len(words(3, 3))
    before = space.work['pair_checks']
    space.choose_probe(ids, 'disagreement', 3, set())
    assert space.work['pair_checks'] - before == 3 * len(words(3, 3))


def test_exact_product_counterexample_goes_beyond_probe_bank():
    rows = tuple(tuple((min(s + 1, 4), 1 if s == 3 else 0) for _ in range(3)) for s in range(5))
    source_model = Machine('long', rows)
    altered = tuple(tuple((min(s + 1, 4), 2 if s == 3 else 0) for _ in range(3)) for s in range(5))
    target = Machine('altered', altered)
    adapter = Adapter(0, (0, 1, 2), (0, 1, 2, 3))
    assert all(source_model.trace(w) == target.trace(w) for w in words(3, 3))
    comparison = compare_adapter(source_model, adapter, target)
    assert not comparison['equivalent']
    assert comparison['counterexample'] == [0, 0, 0, 0]
    assert comparison['visited_pairs'] >= 4
    assert compare_adapter(source_model, adapter, source_model)['equivalent']


def test_observational_equivalence_is_exact_beyond_39_probes():
    rows = tuple(tuple((min(s + 1, 4), 1 if s == 3 else 0) for _ in range(3)) for s in range(5))
    space = CandidateSpace(Machine('long', rows), Contract())
    ids = (aid(space), aid(space, outputs=(0, 2, 1, 3)))
    assert all(space.predict(ids[0], w) == space.predict(ids[1], w) for w in words(3, 3))
    assert space.ambiguity(ids)['observational_classes'] == 2


def test_json_roundtrip_words_and_strict_validation():
    assert Machine.from_dict(source().to_dict()) == source()
    assert Contract.from_dict(Contract().to_dict()) == Contract()
    assert words(2, 2) == ((0,), (1,), (0, 0), (0, 1), (1, 0), (1, 1))
    assert words(3, 0) == ()
    assert Adapter(0, (0, 1, 2), (0, 1, 2, 3)).to_dict()['id'] == 0
    for ctor in (lambda: Machine('x', ()), lambda: Machine('x', (((0, 0),),)),
                 lambda: Machine('x', (((1, 0), (0, 0), (0, 0)),)),
                 lambda: Contract(goal=2, hazard=2), lambda: Contract(horizon=True),
                 lambda: Adapter(0, (0, 0, 2), (0, 1, 2, 3)), lambda: words(True, 2)):
        with pytest.raises((TypeError, ValueError)):
            ctor()
    space = CandidateSpace(source(), Contract())
    for action in (lambda: source().trace((True,)), lambda: space.predict(-1, (0,)),
                   lambda: space.plan((1, True)),
                   lambda: space.survivors([{'word': [0], 'outputs': [], 'complete': True}]),
                   lambda: space.survivors([], {0: 99}), lambda: space.choose_probe((0,), 'bad', 5, set())):
        with pytest.raises((TypeError, ValueError)):
            action()


def test_minimized_observational_classes_match_independent_exact_products():
    rng = random.Random(193)
    for _ in range(4):
        rows = tuple(tuple((rng.randrange(4), rng.randrange(4)) for _ in range(3)) for _ in range(4))
        machine = Machine('random finite model', rows)
        space = CandidateSpace(machine, Contract(horizon=1))
        selected = tuple(rng.sample(range(144), 12))
        representatives = []
        for identifier in selected:
            adapter = space.adapters[identifier]
            mapped = Machine('mapped', tuple(tuple((row[i][0], adapter.output_map[row[i][1]])
                            for i in adapter.input_map) for row in rows))
            if not any(compare_adapter(machine, space.adapters[other], mapped)['equivalent'] for other in representatives):
                representatives.append(identifier)
        assert space.ambiguity(selected)['observational_classes'] == len(representatives)


def test_minimization_collapses_distinct_but_equivalent_reachable_states():
    machine = Machine('duplicate-state terminals', (((1, 1), (2, 2), (0, 0)),
                  ((1, 0), (1, 0), (1, 0)), ((2, 0), (2, 0), (2, 0))))
    space = CandidateSpace(machine, Contract())
    ids = (aid(space), aid(space, inputs=(1, 0, 2), outputs=(0, 2, 1, 3)))
    assert space.ambiguity(ids)['observational_classes'] == 1
