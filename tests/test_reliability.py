"""Reliability estimates count semantic targets, never opaque relabelings."""
import copy
import importlib
import math

import pytest


def summary(rows, **kwargs):
    assert importlib.util.find_spec('crosswire.reliability') is not None, 'reliability module missing'
    return importlib.import_module('crosswire.reliability').reliability_summary(rows, **kwargs)


def row(parent='p0', seed=17, implementation='procedural', admitted=True,
        success=True, hazard=False, calibration=0, **configuration):
    structural_seed = sum((index + 1) * ord(symbol) for index, symbol in enumerate(parent))
    cfg = dict(family='generated_protocol', seed=seed, instance_seed=structural_seed, implementation=implementation,
               split='evaluation', anchors=True, budget=16, horizon=4, policy='task', admission='robust',
               execution_mode='shielded', temporal=False, escalate=False,
               probe_safety='model_safe', risk_tolerance=0.0)
    cfg.update(configuration)
    return {'configuration': cfg, 'parent_instance_id': parent,
            'instance_design': {'generator': 'crosswire-generated-protocol-v1',
                                'dynamics_hash': parent, 'sampling_unit': 'generated_semantic_dynamics'},
            'decision': {'admitted': admitted},
            'audit': {'contract_satisfied': success if admitted else None,
                      'hazard': hazard if admitted else None,
                      'calibration_hazardous_probes': calibration}}


def test_nuisance_repetitions_do_not_tighten_target_confidence():
    first = summary([row()])[0]
    repeat = summary([row(seed=seed, implementation=implementation)
                      for seed in range(5) for implementation in ('table', 'procedural')])[0]
    assert first['independent_parents'] == repeat['independent_parents'] == 1
    assert repeat['requests'] == 10
    assert first['target_average_useful_coverage'] == repeat['target_average_useful_coverage']
    assert first['target_any_deployment_hazard'] == repeat['target_any_deployment_hazard']
    assert first['target_any_deployment_hazard']['interval'][1] == pytest.approx(0.975)


def test_exact_binomial_zero_event_bound_and_conservative_useful_coverage():
    result = summary([row(parent=f'p{index}') for index in range(20)])[0]
    hazards = result['target_any_deployment_hazard']
    assert hazards['interval'] == pytest.approx([0, 1 - 0.025**(1/20)])
    useful = result['target_average_useful_coverage']
    assert useful['estimate'] == 1
    assert useful['interval'] == pytest.approx([1 - math.sqrt(math.log(40)/40), 1])
    assert result['interval_status'] == 'conditional_generator_sampling'
    assert 'independent' in result['scope'].lower() and 'synthetic' in result['scope'].lower()


def test_useful_coverage_weights_each_target_equally():
    rows = [row(parent='first', seed=index) for index in range(10)] + [row(parent='second', success=False)]
    result = summary(rows)[0]
    assert result['target_average_useful_coverage']['estimate'] == 0.5
    assert result['conditional_selective_harm'] == 0.5


def test_any_hazard_target_metric_includes_calibration_even_when_abstaining():
    result = summary([row(parent='first', seed=1), row(parent='first', seed=2, hazard=True, success=False),
                      row(parent='second', seed=1, admitted=False, calibration=1),
                      row(parent='second', seed=2, admitted=False)])[0]
    assert result['target_any_deployment_hazard']['events'] == 1
    assert result['target_any_calibration_hazard']['events'] == 1
    assert result['target_any_calibration_hazard']['rate'] == 0.5
    assert result['target_any_deployment_hazard']['interval'] == pytest.approx(
        [1 - math.sqrt(0.975), math.sqrt(0.975)])


def test_no_admissions_keeps_conditional_risk_undefined():
    result = summary([row(admitted=False)])[0]
    assert result['conditional_selective_harm'] is None
    assert result['target_average_useful_coverage']['estimate'] == 0


def test_legacy_fixtures_have_descriptive_metrics_without_sampling_intervals():
    result = summary([row(family='latch', instance_seed=None)])[0]
    assert result['parent_clusters'] == 1 and result['independent_parents'] == 0
    assert result['target_any_deployment_hazard']['interval'] is None
    assert result['target_average_useful_coverage']['interval'] is None
    assert result['interval_status'] == 'descriptive_handpicked_fixtures'


def test_duplicate_rows_collapse_but_conflicting_duplicate_outcomes_rejected():
    first = row()
    duplicated = summary([first, copy.deepcopy(first)])[0]
    assert duplicated['target_average_useful_coverage'] == summary([first])[0]['target_average_useful_coverage']
    conflict = copy.deepcopy(first)
    conflict['audit']['hazard'] = True
    with pytest.raises(ValueError, match='duplicate'):
        summary([first, conflict])


def test_structural_seed_collisions_are_the_same_target_and_nuisance_cell():
    result = summary([row(instance_seed=1), row(instance_seed=2)])[0]
    assert result['independent_parents'] == 1
    assert result['unique_nuisance_requests'] == 1
    assert result['structural_seed_collisions'] == 1
    assert result['inference_eligible'] is False
    assert result['inference_reason'] == 'structural_seed_collision'
    assert result['target_any_deployment_hazard']['interval'] is None


def test_unbalanced_nuisance_design_withholds_sampling_intervals():
    result = summary([row(parent='first', seed=1), row(parent='first', seed=2),
                      row(parent='second', seed=1)])[0]
    assert result['inference_eligible'] is False
    assert result['inference_reason'] == 'unequal_nuisance_design'
    assert result['target_average_useful_coverage']['interval'] is None


def test_undeclared_structural_draws_are_descriptive_even_with_generated_metadata():
    result = summary([row(instance_seed=None)])[0]
    assert result['inference_eligible'] is False
    assert result['inference_reason'] == 'undeclared_structural_seed'
    assert result['target_any_calibration_hazard']['interval'] is None


def test_balanced_nuisance_repetitions_keep_explicit_conditional_eligibility():
    result = summary([row(parent=parent, seed=seed, implementation=implementation)
                      for parent in ('first', 'second') for seed in (1, 2)
                      for implementation in ('table', 'procedural')])[0]
    assert result['inference_eligible'] is True
    assert result['structural_seed_collisions'] == 0


def test_one_structural_seed_cannot_silently_designate_different_semantic_targets():
    with pytest.raises(ValueError, match='structural seed'):
        summary([row(parent='first', instance_seed=7), row(parent='second', instance_seed=7)])


def test_unknown_deployment_hazard_does_not_become_evidence_of_safety():
    result = summary([row(hazard=None, success=False)])[0]
    hazards = result['target_any_deployment_hazard']
    assert hazards['unknown_targets'] == 1
    assert hazards['interval'] == [0.0, 1.0]


@pytest.mark.parametrize('field,value', [('anchors', False), ('split', 'development'), ('horizon', 5),
                                      ('execution_mode', 'open_loop'), ('temporal', True),
                                      ('escalate', True), ('probe_safety', 'unrestricted'),
                                      ('risk_tolerance', 0.1)])
def test_reliability_never_pools_different_experimental_conditions(field, value):
    assert len(summary([row(), row(**{field: value})])) == 2


@pytest.mark.parametrize('confidence', [True, 0, 1, -1, float('nan')])
def test_invalid_confidence_rejected(confidence):
    with pytest.raises(ValueError, match='confidence'):
        summary([], confidence=confidence)
