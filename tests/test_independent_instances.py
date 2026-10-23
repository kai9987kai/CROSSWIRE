"""Structural instances must vary dynamics without inflating nuisance repeats."""
import itertools
import random

import pytest

from crosswire import fixtures
from crosswire.core import Machine


def generated(**values):
    return fixtures.make_case('generated_protocol', instance_seed=values.pop('instance_seed', 7), **values)


def test_generated_instances_keep_private_structure_and_maps_out_of_metadata():
    state = random.getstate()
    case = generated()
    assert random.getstate() == state
    design = case.public['instance_design']
    assert design['sampling_unit'] == 'generated_semantic_dynamics'
    assert set(design) == {'generator', 'dynamics_hash', 'sampling_unit'}
    assert len(design['dynamics_hash']) == 64
    assert 'reference' not in case.private and 'transitions' not in case.private
    assert 'instance_seed' not in design and 'input_map' not in design
    assert next(row for row in fixtures.catalog() if row['id'] == 'generated_protocol')['scope'] == 'in_family'


def test_structural_identity_excludes_opaque_labels_and_implementation():
    cases = [generated(seed=label, implementation=implementation)
             for label in (4, 19) for implementation in ('table', 'procedural')]
    assert len({c.public['parent_instance_id'] for c in cases}) == 1
    assert len({c.public['target_id'] for c in cases}) == 4
    assert all(c.public['reference'] == cases[0].public['reference'] for c in cases)


def test_structural_seeds_vary_reachable_dynamics_and_preserve_horizon_four_feasibility():
    cases = [generated(instance_seed=value) for value in range(24)]
    assert len({c.public['parent_instance_id'] for c in cases}) >= 16
    for case in cases:
        plan = fixtures.oracle_plan(case.private, horizon=4)
        assert plan is not None and len(plan) in (3, 4)
        assert fixtures.evaluate_word(case.private, plan)['contract_satisfied']
        # All first and second actions are safe, independent of raw labels.
        for word in itertools.product(range(3), repeat=2):
            assert not fixtures.evaluate_word(case.private, word)['hazard']


def test_generated_engines_match_every_reachable_transition_and_reference():
    for instance in (0, 7, 19):
        cases = [generated(instance_seed=instance, seed=31, implementation=kind, anchors=True)
                 for kind in ('table', 'procedural')]
        models = [fixtures.target_machine(case.private) for case in cases]
        assert models[0].transitions == models[1].transitions
        for case, model in zip(cases, models):
            reference = Machine.from_dict(case.public['reference'])
            observed_anchors = set()
            for length in range(1, 5):
                for word in itertools.product(range(3), repeat=length):
                    result = fixtures.evaluate_word(case.private, word)
                    semantic_word = [case.private['input_map'][symbol] for symbol in word]
                    assert result['semantic_events'] == list(reference.trace(semantic_word))
                    assert tuple(result['outputs']) == model.trace(word)
                    for raw, actual in zip(result['outputs'], result['semantic_events']):
                        if raw in case.public['anchors']:
                            assert case.public['anchors'][raw] == actual
                            observed_anchors.add(raw)
            assert case.public['anchors'] and observed_anchors == set(case.public['anchors'])


def test_procedural_generated_target_does_not_read_reference_table(monkeypatch):
    case = generated()
    def forbidden(*args, **kwargs):
        raise AssertionError('procedural target consumed a materialized reference')
    monkeypatch.setattr(fixtures, '_protocol_table', forbidden)
    assert fixtures.oracle_plan(case.private, 4) is not None
    assert fixtures.target_machine(case.private) is not None


def test_inert_generator_parameter_differences_cannot_inflate_parent_count(monkeypatch):
    parameters = generated().private['mechanism_parameters']
    monkeypatch.setattr(fixtures, '_protocol_parameters',
                        lambda seed: dict(parameters, ignored_annotation=str(seed)))
    first, second = generated(instance_seed=1), generated(instance_seed=2)
    assert first.public['parent_instance_id'] == second.public['parent_instance_id']
    assert first.public['reference'] == second.public['reference']


@pytest.mark.parametrize('seed', [True, -1, 2**32, 1.5, '7'])
def test_structural_seed_validation(seed):
    with pytest.raises(ValueError, match='instance_seed'):
        generated(instance_seed=seed)


def test_legacy_fixtures_cannot_claim_structural_seed_independence():
    with pytest.raises(ValueError, match='instance_seed'):
        fixtures.make_case('latch', instance_seed=2)
    assert set(fixtures.make_case('latch').public) == {
        'reference', 'contract', 'target_id', 'anchors', 'parent_instance_id'}
