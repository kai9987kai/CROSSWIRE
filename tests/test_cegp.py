import pytest
from crosswire.core import CandidateSpace, Contract, Machine


def _machine():
    transitions = (((1, 0), (0, 3), (1, 2)), ((1, 1), (1, 1), (1, 2)))
    return Machine("test", transitions, 3, 4, 0)


def test_cegp_policy_selects_distinguishing_probe():
    m = _machine()
    c = Contract(goal=1, hazard=2, horizon=4)
    space = CandidateSpace(m, c)
    survivors = tuple(range(10))  # subset of adapters
    seen = set()
    probe = space.choose_probe(survivors, "counterexample", remaining_steps=3, seen=seen)
    assert probe is not None
    assert 1 <= len(probe) <= 3
    # Check that the probe actually separates at least two surviving adapters
    preds = {aid: space.predict(aid, probe) for aid in survivors}
    assert len(set(preds.values())) > 1


def test_cegp_respects_remaining_steps_and_seen():
    m = _machine()
    c = Contract(goal=1, hazard=2, horizon=4)
    space = CandidateSpace(m, c)
    survivors = (0, 1, 2)
    seen = {(0,), (1,), (2,)}
    probe = space.choose_probe(survivors, "counterexample", remaining_steps=1, seen=seen)
    # Since all 1-symbol words are seen, and remaining_steps=1, no eligible probe remains
    assert probe is None
