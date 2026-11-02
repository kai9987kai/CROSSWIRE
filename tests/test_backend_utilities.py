"""Backend selection, exact task scoring and bounded finite product planning."""
from fractions import Fraction
import importlib
from itertools import combinations

import pytest

import crosswire.core as core
from crosswire.core import CandidateSpace, Contract, FactoredCandidateSpace, Machine
from crosswire.fixtures import make_case


def _space(space_type=FactoredCandidateSpace, family='latch', temporal=False, horizon=4):
    case = make_case(family, horizon=horizon)
    return space_type(Machine.from_dict(case.public['reference']),
                      Contract.from_dict(case.public['contract']), temporal=temporal)


def _backends():
    assert importlib.util.find_spec('crosswire.backends') is not None, 'backend factory is missing'
    return importlib.import_module('crosswire.backends')


def test_backend_factory_defaults_and_reports_actual_storage_without_materialization():
    backends = _backends()
    source = _space()
    assert backends.CANDIDATE_BACKENDS == ('flat', 'factored')
    flat = backends.make_space(source.machine, source.contract)
    factored = backends.make_space(source.machine, source.contract, backend='factored', temporal=True)
    assert type(flat) is CandidateSpace
    assert type(factored) is FactoredCandidateSpace
    factored.predict(0, (0,))
    factored.adapter(0)
    summary = backends.backend_summary(factored, (0, 1))
    assert summary['backend'] == 'factored'
    assert summary['total_candidates'] == 720
    assert summary['active_candidates'] == 2
    assert summary['total_input_factors'] == 6
    assert summary['total_output_factors'] == 24
    assert summary['active_input_factors'] == 1
    assert summary['active_output_factors'] == 2
    assert summary['cached_adapters'] == 1
    assert summary['cached_predictions'] == 1
    assert summary['structural_ratio'] == 24.0
    assert 'not measured memory' in summary['structural_ratio_scope'].lower()
    assert len(factored._adapter_cache) == 1
    flat_summary = backends.backend_summary(flat, ())
    assert flat_summary['backend'] == 'flat'
    assert flat_summary['cached_adapters'] == 144
    assert flat_summary['active_candidates'] == 0


@pytest.mark.parametrize('backend', ['unknown', True, None, 1])
def test_backend_factory_rejects_unsupported_labels(backend):
    source = _space()
    with pytest.raises(ValueError, match='backend'):
        _backends().make_space(source.machine, source.contract, backend=backend)


def test_factored_predictions_cache_raw_expansions_across_equivalent_word_types():
    space = _space(temporal=True)
    first = space.predict(145, [0, 1, 0])
    before = dict(space.work)
    assert space.predict(145, (0, 1, 0)) == first
    assert space.work == before
    assert len(space._predictions) == 1


@pytest.mark.parametrize('identifier', [True, False, 1.0, 0.0])
def test_factored_adapter_validates_ids_before_cached_alias_lookup(identifier):
    space = _space()
    space.adapter(0)
    space.adapter(1)
    with pytest.raises(TypeError, match='adapter id'):
        space.adapter(identifier)


@pytest.mark.parametrize('arguments', [(-1, 0), (6, 0), (0, 24), (True, 0),
                                       (0, 0, 2), (0, 0, 0, 1), (0, 0, 1, 4)])
def test_factored_composition_rejects_noncanonical_or_invalid_factors(arguments):
    with pytest.raises((ValueError, TypeError)):
        _space(temporal=True).compose_id(*arguments)


def test_static_factored_space_cannot_compose_a_temporal_candidate():
    with pytest.raises(ValueError, match='temporal'):
        _space().compose_id(0, 0, delay=1)


def _pairwise_task_choice(space, ids, remaining, seen):
    best, best_score = None, Fraction(0)
    for word in space._probes:
        if len(word) > remaining or word in seen:
            continue
        score = Fraction(0)
        for left, right in combinations(ids, 2):
            left_safe, right_safe = space.safe_words(left), space.safe_words(right)
            if space.predict(left, word) != space.predict(right, word):
                score += Fraction(len(left_safe ^ right_safe), max(1, len(left_safe | right_safe)))
        score /= 1 + len(word)
        if score > best_score:
            best, best_score = word, score
    return best


@pytest.mark.parametrize('space_type', [CandidateSpace, FactoredCandidateSpace])
@pytest.mark.parametrize('temporal', [False, True])
def test_task_histogram_choice_matches_independent_pairwise_fraction_oracle(space_type, temporal):
    space = _space(space_type, family='handshake', temporal=temporal)
    ids = (0, 1, 24, 25, 48, 49, 96, 97) + ((144, 145, 240, 241) if temporal else ())
    seen = {(0,)}
    expected = _pairwise_task_choice(space, ids, 2, seen)
    assert expected is not None
    assert space.choose_probe(ids, 'task', 2, seen) == expected


def test_task_scoring_never_constructs_candidate_pair_tuple(monkeypatch):
    def forbidden_pairs(*args, **kwargs):
        raise AssertionError('quadratic candidate pair allocation')

    monkeypatch.setattr(core, 'combinations', forbidden_pairs, raising=False)
    assert _space().choose_probe(tuple(range(144)), 'task', 1, set()) is not None


@pytest.mark.parametrize('space_type', [CandidateSpace, FactoredCandidateSpace])
def test_exact_task_tie_prefers_shortest_lexicographic_query(space_type):
    # The exact scores of (0,), (1,) and (0, 0) are all 8. Summing the
    # per-candidate float weights used to select the longer word (0, 0).
    rows = (((0, 0), (1, 1)), ((0, 2), (2, 0)), ((0, 1), (0, 0)))
    space = space_type(Machine('exact_score_tie', rows, inputs=2, outputs=3), Contract(horizon=3))
    assert space.choose_probe(tuple(range(12)), 'task', 3, set()) == (0,)


@pytest.mark.parametrize('space_type', [CandidateSpace, FactoredCandidateSpace])
def test_task_with_one_contract_class_still_abstains(space_type):
    space = _space(space_type)
    assert space.choose_probe((0, 1, 2, 3), 'task', 3, set()) is None


def test_factored_deployment_words_are_lazy_but_keep_compatible_accessor(monkeypatch):
    lengths = []
    original = core.words

    def recorded_words(inputs, max_length):
        lengths.append(max_length)
        return original(inputs, max_length)

    monkeypatch.setattr(core, 'words', recorded_words)
    machine = Machine('two_actions', (((0, 0), (0, 1)),), inputs=2, outputs=3)
    space = FactoredCandidateSpace(machine, Contract(horizon=6))
    assert 6 not in lengths
    assert space.plan((0,))['word'] == [1]
    assert 6 not in lengths
    assert len(space._deployment) == 126
    assert lengths.count(6) == 1


@pytest.mark.parametrize('family', ['latch', 'routing', 'neutral', 'handshake', 'interlock'])
@pytest.mark.parametrize('temporal', [False, True])
def test_factored_product_search_matches_exhaustive_flat_robust_plan(family, temporal):
    flat, factored = _space(CandidateSpace, family, temporal), _space(FactoredCandidateSpace, family, temporal)
    for ids in ((0,), (0, 24), tuple(range(24)), flat.survivors([])):
        assert factored.plan(ids) == flat.plan(ids)


def test_factored_product_search_checks_goal_before_pruning_visited_initial_state():
    machine = Machine('goal_self_loop', (((0, 0),), ((1, 1),)), inputs=1, outputs=3, initial=1)
    space = FactoredCandidateSpace(machine, Contract(horizon=3))
    assert space.plan((0,))['word'] == [0]


def test_factored_search_limit_is_incomplete_and_does_not_poison_later_search():
    machine = Machine('two_step_goal', (((1, 0),), ((1, 1),)), inputs=1, outputs=3)
    space = FactoredCandidateSpace(machine, Contract(horizon=2))
    limited = space.plan((0,), node_limit=1)
    assert limited['status'] == 'SEARCH_LIMIT'
    assert limited['admitted'] is False
    assert limited['search']['complete'] is False
    assert space.plan((0,), node_limit=2)['word'] == [0, 0]
    work = dict(space.work)
    assert space.plan((0,))['word'] == [0, 0]
    assert space.work == work


@pytest.mark.parametrize('node_limit', [0, -1, True, 1.5])
def test_factored_search_validates_limits_even_for_empty_beliefs(node_limit):
    with pytest.raises((TypeError, ValueError)):
        _space().plan((), node_limit=node_limit)


def test_factored_search_cancellation_is_checked_before_cached_answers():
    from crosswire.study import Cancelled

    space = _space(family='neutral')
    space.plan((0,))
    with pytest.raises(Cancelled):
        space.plan((0,), cancel=lambda: True)


def test_factored_search_cancellation_during_expansion_does_not_cache_partial_answer():
    from crosswire.study import Cancelled

    machine = Machine('two_step_goal', (((1, 0),), ((1, 1),)), inputs=1, outputs=3)
    space = FactoredCandidateSpace(machine, Contract(horizon=2))
    calls = 0

    def cancel_after_first_expansion():
        nonlocal calls
        calls += 1
        return calls == 4

    with pytest.raises(Cancelled):
        space.plan((0,), cancel=cancel_after_first_expansion)
    assert space.plan((0,))['word'] == [0, 0]
