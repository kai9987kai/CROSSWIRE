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


def test_cegp_synthesizes_extended_distinguishing_witness_beyond_pool():
    from crosswire.fixtures import make_case
    case = make_case("long_trace", seed=17)
    space = CandidateSpace(Machine.from_dict(case.public["reference"]), Contract.from_dict(case.public["contract"]))
    # In long_trace, adapters 4 and 65 only differ at length 4 (transitions after 3 advances)
    # Standard 3-step probes cannot distinguish them:
    for w in space._probes:
        assert space.predict(4, w) == space.predict(65, w)
    # But distinguishing_word finds the 4-step witness!
    witness = space.distinguishing_word(4, 65, max_length=6)
    assert witness is not None
    assert len(witness) == 4
    assert space.predict(4, witness) != space.predict(65, witness)
    # And choose_probe with counterexample policy selects it when given remaining_steps >= 4!
    seen = set(space._probes)
    probe = space.choose_probe((4, 65), "counterexample", remaining_steps=4, seen=seen)
    assert probe is not None
    assert len(probe) == 4
    assert space.predict(4, probe) != space.predict(65, probe)

