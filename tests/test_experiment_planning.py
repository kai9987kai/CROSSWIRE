"""Small exact models expose planning objectives and bounded-search behavior."""
import pytest

from crosswire.experiments import synthesize_experiment


class SmallBelief:
    """Four deterministic models with two task classes and a cheap decoy test."""
    _probes = ((0,), (1, 1))
    work = None

    def __init__(self):
        self.work = {'source_steps': 0, 'candidate_expansions': 0, 'pair_checks': 0}

    def _ids(self, ids):
        return tuple(sorted(set(ids)))

    def predict(self, identifier, word):
        bit = identifier % 2 if word == (0,) else identifier // 2
        return (bit,) * len(word)

    def plan(self, ids, mode):
        ready = bool(ids) and len({identifier // 2 for identifier in ids}) == 1
        return {'admitted': ready, 'word': [2] if ready else None, 'status': 'TASK_ADMISSIBLE' if ready else 'UNRESOLVED'}

    def probe_is_safe(self, ids, word):
        return word != (0,)


def test_task_readiness_beats_cheaper_information_when_only_one_query_fits():
    planned = synthesize_experiment(SmallBelief(), range(4), 3)
    assert planned['word'] == [1, 1]
    assert planned['objective']['ready_models'] == 4
    assert planned['objective']['worst_case_calls'] == 3  # Includes reset.
    assert planned['search_complete'] is True


def test_two_queries_obey_actual_reset_plus_action_cap():
    planned = synthesize_experiment(SmallBelief(), range(4), 4)
    assert planned['objective']['worst_case_calls'] <= 4
    assert planned['depth_limit'] == 2
    assert planned['tree']['kind'] == 'query'


def test_safe_selection_seen_queries_and_no_affordable_query():
    planned = synthesize_experiment(SmallBelief(), range(4), 3, safe_only=True)
    assert planned['word'] == [1, 1]
    assert synthesize_experiment(SmallBelief(), range(4), 3, seen={(1, 1)}, safe_only=True)['word'] is None
    assert synthesize_experiment(SmallBelief(), range(4), 1)['word'] is None
    assert synthesize_experiment(SmallBelief(), (), 3)['word'] is None


def test_search_limit_is_honest_and_fallback_tree_is_complete():
    planned = synthesize_experiment(SmallBelief(), range(4), 5, node_limit=1)
    assert planned['search_complete'] is False
    assert planned['expanded_nodes'] <= 1
    assert planned['selection'] == 'one_query_fallback'
    assert planned['word'] is not None
    assert set(planned['tree']['branches']) == {'[0,0]', '[1,1]'}


def test_cancellation_is_observed_without_dispatch():
    from crosswire.study import Cancelled
    with pytest.raises(Cancelled):
        synthesize_experiment(SmallBelief(), range(4), 8, cancel=lambda: True)


@pytest.mark.parametrize('value', [True, -1, 513, 1.5])
def test_invalid_call_budget_is_rejected(value):
    with pytest.raises((TypeError, ValueError)):
        synthesize_experiment(SmallBelief(), range(4), value)


def test_root_objective_retains_branch_alternatives_when_another_branch_dominates_maximum():
    class CoupledBelief(SmallBelief):
        _probes = ((0,), (1,), (2, 2), (1, 1))

        def plan(self, ids, mode):
            return {'admitted': False, 'word': None, 'status': 'UNRESOLVED'}

        def predict(self, i, word):
            if word == (0,):
                return (int(i >= 8),)
            if word == (1,):
                return (i // 3,) if i < 8 else (0,)
            if word == (1, 1):
                return (i // 3, 0) if i < 8 else (0, int(i >= 13))
            return (0, 0) if i < 4 or i >= 8 else ((0, 1), (1, 0), (1, 1), (2, 0))[i - 4]

    planned = synthesize_experiment(CoupledBelief(), range(18), 5)
    # A's 4/1/1/1/1 partition beats 3/3/2 in the whole tree because B
    # already imposes a five-model worst leaf. The square sums are 70 vs72.
    assert planned['search_complete'] is True
    assert planned['word'] == [0]
    assert planned['objective'] == {'ready_models': 0, 'largest_unresolved_belief': 5,
                                    'terminal_squared_beliefs': 70, 'worst_case_calls': 5}
    assert planned['tree']['branches']['[0]']['word'] == [2, 2]


@pytest.mark.parametrize('temporal', [False, True])
def test_readiness_collapses_only_semantically_identical_input_factors_and_keeps_model_weights(temporal):
    from crosswire.core import CandidateSpace, Contract, Machine
    from crosswire.fixtures import make_case
    from crosswire.experiment_checks import verify_experiment_tree
    case = make_case('latch')
    space = CandidateSpace(Machine.from_dict(case.public['reference']), Contract.from_dict(case.public['contract']), temporal=temporal)
    original = space.plan
    checked_sizes = []
    def tracked(ids, mode):
        checked_sizes.append(len(ids))
        return original(ids, mode)
    space.plan = tracked
    size = len(space.adapters)
    planned = synthesize_experiment(space, range(size), 2)
    assert max(checked_sizes) <= 6
    certificate = verify_experiment_tree(case.public['reference'], case.public['contract'], planned['tree'], budget=2, temporal=temporal)
    assert certificate['valid'] is True
    assert certificate['candidate_count'] == size
    for key, value in planned['objective'].items():
        assert certificate[key] == value


def test_large_temporal_tree_preserves_the_full_model_objective_with_lazy_materialization():
    from crosswire.core import CandidateSpace, Contract, Machine
    from crosswire.fixtures import make_case
    from crosswire.experiment_checks import verify_experiment_tree
    case = make_case('latch')
    space = CandidateSpace(Machine.from_dict(case.public['reference']), Contract.from_dict(case.public['contract']), temporal=True)
    planned = synthesize_experiment(space, range(720), 16)
    expected = {'ready_models': 720, 'largest_unresolved_belief': 0,
                'terminal_squared_beliefs': 1536, 'worst_case_calls': 8}
    assert planned['search_complete'] is True
    assert planned['objective'] == expected
    certificate = verify_experiment_tree(case.public['reference'], case.public['contract'], planned['tree'],
                                          temporal=True, budget=16)
    assert certificate['valid'] is True
    for key, value in expected.items():
        assert certificate[key] == value
