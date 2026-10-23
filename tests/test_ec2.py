import pytest
from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.fixtures import make_case
from crosswire.interfaces import TargetProcess
from crosswire.study import RunConfig, run


def test_ec2_policy_accepted_by_choose_probe():
    case = make_case('latch', seed=42)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']))
    survivors = tuple(a.id for a in space.adapters)
    probe = space.choose_probe(survivors, 'ec2', remaining_steps=3, seen=set())
    assert probe is not None
    assert isinstance(probe, tuple)
    assert len(probe) <= 3
    assert all(0 <= a < space.machine.inputs for a in probe)


def test_ec2_avoids_seen_probes_and_respects_step_budget():
    case = make_case('latch', seed=42)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']))
    survivors = tuple(a.id for a in space.adapters)
    probe1 = space.choose_probe(survivors, 'ec2', remaining_steps=3, seen=set())
    assert probe1 is not None
    probe2 = space.choose_probe(survivors, 'ec2', remaining_steps=3, seen={probe1})
    assert probe2 != probe1

    # Length strictly bounded by remaining_steps
    short_probe = space.choose_probe(survivors, 'ec2', remaining_steps=1, seen=set())
    assert short_probe is not None
    assert len(short_probe) == 1


def test_ec2_returns_none_or_shortest_when_all_survivors_in_single_decision_class():
    case = make_case('neutral', seed=42)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']))
    # For neutral fixture, find a subset of adapters that share the exact same safe_words
    classes = space._decision_classes(tuple(a.id for a in space.adapters))
    largest_class = max(classes, key=lambda c: len(c[1]))
    survivors = tuple(largest_class[1])
    # When all survivors agree on contract safe words, cross-class edge cutting is 0
    probe = space.choose_probe(survivors, 'ec2', remaining_steps=3, seen=set())
    # Should either return a fallback distinguishing probe or None, without raising an exception
    if probe is not None:
        assert len(probe) <= 3


def test_ec2_active_probing_resolves_latch_within_budget():
    config = RunConfig(family='latch', seed=42, budget=16, policy='ec2', admission='robust')
    result = run(config)
    assert result['schema'] == 'crosswire-result-v1'
    assert result['decision']['admitted'] is True
    assert result['audit']['contract_satisfied'] is True
    assert result['audit']['hazard'] is False
    assert result['metrics']['target_calls'] <= 16
    assert result['metrics']['target_calls'] > 0


def test_ec2_with_temporal_hypothesis_space():
    case = make_case('latch', seed=42)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']),
                           temporal=True)
    assert len(space.adapters) == 720
    survivors = tuple(a.id for a in space.adapters[:100])
    probe = space.choose_probe(survivors, 'ec2', remaining_steps=3, seen=set())
    assert probe is not None
    assert len(probe) <= 3


def test_ec2_rotary_and_handshake():
    for fam in ('rotary', 'handshake'):
        config = RunConfig(family=fam, seed=17, budget=16, policy='ec2', admission='robust')
        result = run(config)
        assert result['schema'] == 'crosswire-result-v1'
        assert result['audit']['hazard'] is False
