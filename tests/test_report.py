"""Saved report rendering must preserve experimental strata and acquisition harm."""
from copy import deepcopy

import pytest

from crosswire.identity import canonical_hash, scientific_view
from tools.report import render


def _summary(family='latch', scope='in_family', requests=2, **changes):
    row = {'family': family, 'scope': scope, 'method': 'task/robust', 'budget': 16,
           'requests': requests, 'admitted': requests, 'successful': requests,
           'harmful': 0, 'hazardous': 0, 'hazards_averted': 0, 'shield_interventions': 0,
           'interface_errors': 0, 'abstained': 0, 'oracle_feasible': requests,
           'calibration_hazardous_runs': 1, 'calibration_hazardous_probes': 3,
           'mean_target_calls': 6.0, 'mean_deployment_calls': 2.0, 'mean_total_calls': 8.0,
           'mean_target_steps': 5.0, 'mean_resets': 1.0,
           'probe_safety': 'unrestricted', 'risk_tolerance': 0.0,
           'execution_mode': 'open_loop', 'anchors': False, 'split': 'development',
           'horizon': 4, 'temporal': False, 'escalate': False}
    return {**row, **changes}


def _receipt(summary, paired=None):
    receipt = {'schema': 'crosswire-receipt-v1', 'source_hash': 'a' * 64,
               'payload': {'schema': 'crosswire-study-v1', 'source_hash': 'a' * 64,
                           'protocol': {}, 'protocol_hash': canonical_hash({}),
                           'rows': [{'parent_instance_id': f'p{i}', 'baseline': {}}
                                    for i, _ in enumerate(summary)],
                           'summary': summary, 'paired': paired or []}}
    return _seal(receipt)


def _seal(receipt):
    """Seal deliberately edited test data without requiring the current source."""
    receipt['payload']['scientific_hash'] = canonical_hash(scientific_view(receipt['payload']))
    receipt['payload_hash'] = canonical_hash(receipt['payload'])
    return receipt


def _table(text, heading):
    section = text.split(heading, 1)[1].split('### ', 1)[0]
    lines = [line for line in section.splitlines() if line.startswith('|')]
    header = [cell.strip() for cell in lines[0].strip('|').split('|')]
    return [dict(zip(header, (cell.strip() for cell in line.strip('|').split('|'))))
            for line in lines[2:]]


def test_report_pools_only_within_identical_conditions_and_scope():
    entries = [_summary(), _summary('handshake', requests=4, mean_target_calls=12,
                                   mean_deployment_calls=4, mean_total_calls=16,
                                   calibration_hazardous_runs=2, calibration_hazardous_probes=5),
               _summary(probe_safety='model_safe', calibration_hazardous_runs=0,
                        calibration_hazardous_probes=0),
               _summary(risk_tolerance=0.2),
               _summary('control', 'control'), _summary('stress', 'out_of_family')]
    receipt = _receipt(entries)
    before = deepcopy(receipt)
    rendered = render(receipt, 'Stratified results')
    aggregate = _table(rendered, '### Method')
    assert len(aggregate) == 5
    assert {row['Scope'] for row in aggregate} == {'in_family', 'control', 'out_of_family'}
    pooled = next(row for row in aggregate
                  if row['Scope'] == 'in_family' and row['Requests'] == '6')
    assert pooled['Hazardous calibration runs'] == '3'
    assert pooled['Hazardous calibration probes'] == '8'
    assert pooled['Mean calibration calls'] == '10.0'
    assert pooled['Mean deployment calls'] == '3.3'
    assert pooled['Mean total calls'] == '13.3'
    assert 'probe_safety=unrestricted' in pooled['Conditions']
    assert 'risk_tolerance=0' in pooled['Conditions']
    safe = next(row for row in aggregate if 'probe_safety=model_safe' in row['Conditions'])
    assert safe['Hazardous calibration probes'] == '0'
    assert any('risk_tolerance=0.2' in row['Conditions'] for row in aggregate)
    assert receipt == before


def test_every_execution_condition_is_visible_and_keeps_aggregates_separate():
    changes = [{'execution_mode': 'shielded'}, {'anchors': True}, {'split': 'evaluation'},
               {'horizon': 6}, {'temporal': True}, {'escalate': True}]
    entries = [_summary(), *(_summary(**change) for change in changes)]
    rendered = render(_receipt(entries), 'Conditions')
    aggregate = _table(rendered, '### Method')
    family = _table(rendered, '### Per family')
    assert len(aggregate) == len(entries) == len(family)
    for change in changes:
        key, value = next(iter(change.items()))
        label = f'{key}={str(value).lower() if type(value) is bool else value}'
        assert any(label in row['Conditions'] for row in aggregate)
        assert any(label in row['Conditions'] for row in family)
    assert all('Hazardous calibration runs' in row and 'Mean calibration calls' in row for row in family)


def test_paired_tables_show_saved_conditions_scope_and_fixed_comparison_rule():
    pair = {'contrast': 'entropy - fixed', 'budget': 16, 'parent_clusters': 2,
            'matched_cells': 4, 'mean_delta': 0.5, 'descriptive_95_interval': [0, 1],
            'probe_safety': 'model_safe', 'risk_tolerance': 0.2,
            'execution_mode': 'replan', 'anchors': True, 'split': 'evaluation',
            'horizon': 6, 'temporal': True, 'escalate': False,
            'comparison_axis': 'policy', 'fixed_admission': 'risk_controlled',
            'families_pooled': ['handshake', 'latch'], 'scope': 'saved in-family paired scope'}
    rendered = render(_receipt([_summary()], [pair]), 'Pairs')
    row = _table(rendered, '### Paired')[0]
    assert row['Scope'] == pair['scope']
    assert row['Families'] == 'handshake, latch'
    assert row['Fixed rule'] == 'admission=risk_controlled'
    for label in ('probe_safety=model_safe', 'risk_tolerance=0.2', 'execution_mode=replan',
                  'anchors=true', 'split=evaluation', 'horizon=6', 'temporal=true', 'escalate=false'):
        assert label in row['Conditions']


def test_legacy_call_means_are_named_and_unknown_deployment_cost_is_not_zero():
    entry = _summary()
    for key in ('mean_target_calls', 'mean_deployment_calls', 'mean_total_calls'):
        entry.pop(key)
    rendered = render(_receipt([entry]), 'Legacy')
    row = _table(rendered, '### Method')[0]
    assert row['Mean calibration calls'] == '6.0'
    assert row['Mean deployment calls'] == 'n/a'
    assert row['Mean total calls'] == 'n/a'


def test_legacy_summary_recovers_execution_conditions_from_its_saved_run_rows():
    summary = _summary()
    summary.pop('execution_mode')
    receipt = _receipt([summary])
    receipt['payload']['rows'][0]['configuration'] = {
        'family': 'latch', 'policy': 'task', 'admission': 'robust', 'budget': 16,
        'execution_mode': 'shielded'}
    _seal(receipt)
    row = _table(render(receipt, 'Legacy conditions'), '### Per family')[0]
    assert 'execution_mode=shielded' in row['Conditions']


def test_legacy_summary_cannot_silently_pool_unrecorded_execution_conditions():
    summary = _summary()
    summary.pop('execution_mode')
    receipt = _receipt([summary])
    receipt['payload']['rows'] = [
        {'parent_instance_id': 'p', 'baseline': {}, 'configuration': {
            'family': 'latch', 'policy': 'task', 'admission': 'robust', 'budget': 16,
            'execution_mode': mode}}
        for mode in ('open_loop', 'shielded')]
    _seal(receipt)
    with pytest.raises(ValueError, match='conditions'):
        render(receipt, 'Mixed legacy conditions')


def test_forced_fit_diagnostics_keep_scope_budget_and_conditions():
    receipt = _receipt([_summary(scope='control', method='task/fit', probe_safety='model_safe')])
    receipt['payload']['rows'][0].update(
        configuration={'family': 'latch', 'policy': 'task', 'admission': 'fit', 'budget': 16,
                       'implementation': 'procedural', 'seed': 17, 'probe_safety': 'model_safe'},
        baseline={'fit_diagnostics': {'total_residual': 2, 'raw_mismatches': 1,
                                     'anchor_mismatches': 1, 'maps_tied_at_minimum': 3}},
        audit={'contract_satisfied': False})
    _seal(receipt)
    row = _table(render(receipt, 'Fit'), '### Forced-fit')[0]
    assert row['Scope'] == 'control'
    assert row['Budget'] == '16'
    assert 'probe_safety=model_safe' in row['Conditions']


def _reliability(**changes):
    record = {'family': 'generated_protocol', 'method': 'task/robust', 'budget': 16,
              'anchors': True, 'split': 'evaluation', 'horizon': 6,
              'execution_mode': 'shielded', 'temporal': True, 'escalate': False,
              'probe_safety': 'model_safe', 'risk_tolerance': 0.2,
              'confidence': 0.95, 'requests': 120, 'parent_clusters': 10,
              'independent_parents': 10, 'inference_eligible': True,
              'inference_reason': 'independent_generator_draws_assumed',
              'interval_status': 'conditional_generator_sampling',
              'target_any_deployment_hazard': {'events': 0, 'targets': 10,
                  'unknown_targets': 2, 'rate': 0.0, 'possible_rate': 0.2,
                  'interval': [0, 0.000003688]},
              'target_any_calibration_hazard': {'events': 3, 'targets': 10,
                  'unknown_targets': 0, 'rate': 0.3, 'possible_rate': 0.3,
                  'interval': [0.07, 0.65]},
              'target_average_useful_coverage': {'estimate': 0.75, 'interval': [0.2, 1]},
              'conditional_selective_harm': 0.125,
              'scope': 'Saved synthetic target scope; pointwise bounds assume independent draws.'}
    return {**record, **changes}


def test_reliability_report_preserves_target_denominators_conditions_and_positive_zero_event_upper():
    receipt = _receipt([_summary()])
    receipt['payload']['reliability'] = [_reliability()]
    _seal(receipt)
    before = deepcopy(receipt)
    rendered = render(receipt, 'Reliability')
    design = _table(rendered, '### Reliability design')[0]
    assert design['Row'] == 'R1'
    assert design['Family'] == 'generated_protocol'
    assert design['Requests'] == '120'
    assert design['Parent clusters'] == '10'
    assert design['Independent parents (declared)'] == '10'
    assert design['Inference eligible'] == 'true'
    assert design['Inference reason'] == 'independent_generator_draws_assumed'
    assert design['Interval status'] == 'conditional_generator_sampling'
    for label in ('anchors=true', 'split=evaluation', 'horizon=6', 'execution_mode=shielded',
                  'temporal=true', 'escalate=false', 'probe_safety=model_safe', 'risk_tolerance=0.2'):
        assert label in design['Conditions']
    hazards = _table(rendered, '### Target-cluster hazard bounds')
    deployment = next(row for row in hazards if row['Outcome'] == 'Deployment hazard')
    assert deployment['Row'] == 'R1'
    assert deployment['Events'] == '0' and deployment['Targets'] == '10'
    assert deployment['Unknown targets'] == '2'
    assert deployment['Observed rate'] == '0%'
    assert deployment['Possible rate'] == '20%'
    assert deployment['Confidence'] == '95%'
    assert deployment['Pointwise interval'] == '[0%, 0.0003688%]'
    calibration = next(row for row in hazards if row['Outcome'] == 'Calibration hazard')
    assert calibration['Events'] == '3' and calibration['Targets'] == '10'
    assert calibration['Observed rate'] == '30%'
    useful = _table(rendered, '### Target-cluster useful coverage')[0]
    assert useful['Target-average useful coverage'] == '75%'
    assert useful['Pointwise interval'] == '[20%, 100%]'
    assert useful['Conditional selective harm'] == '12.5%'
    assert receipt['payload']['reliability'][0]['scope'] in rendered
    assert receipt == before


def test_reliability_report_labels_unavailable_intervals_and_undefined_selective_harm():
    receipt = _receipt([_summary()])
    event = {'events': 0, 'targets': 1, 'unknown_targets': 0,
             'rate': 0, 'possible_rate': 0, 'interval': None}
    receipt['payload']['reliability'] = [_reliability(
        family='latch', parent_clusters=1, independent_parents=0,
        inference_eligible=False, inference_reason='handpicked_fixtures',
        interval_status='descriptive_handpicked_fixtures',
        target_any_deployment_hazard=event, target_any_calibration_hazard=event,
        target_average_useful_coverage={'estimate': 0, 'interval': None},
        conditional_selective_harm=None)]
    _seal(receipt)
    rendered = render(receipt, 'Descriptive')
    design = _table(rendered, '### Reliability design')[0]
    assert design['Inference eligible'] == 'false'
    assert design['Inference reason'] == 'handpicked_fixtures'
    assert design['Independent parents (declared)'] == '0'
    assert all(row['Pointwise interval'] == 'unavailable (descriptive)'
               for row in _table(rendered, '### Target-cluster hazard bounds'))
    useful = _table(rendered, '### Target-cluster useful coverage')[0]
    assert useful['Pointwise interval'] == 'unavailable (descriptive)'
    assert useful['Conditional selective harm'] == 'n/a'


def test_reliability_records_keep_different_conditions_and_scopes_visible():
    receipt = _receipt([_summary()])
    first = _reliability()
    second = _reliability(probe_safety='unrestricted', risk_tolerance=0,
                          scope='A different saved scope.')
    receipt['payload']['reliability'] = [first, second]
    _seal(receipt)
    rendered = render(receipt, 'Separate reliability strata')
    design = _table(rendered, '### Reliability design')
    assert len(design) == 2
    assert {row['Row'] for row in design} == {'R1', 'R2'}
    assert any('probe_safety=model_safe' in row['Conditions'] for row in design)
    assert any('probe_safety=unrestricted' in row['Conditions'] for row in design)
    assert first['scope'] in rendered and second['scope'] in rendered


def test_legacy_report_without_reliability_keeps_existing_output():
    receipt = _receipt([_summary()])
    legacy = render(receipt, 'Legacy')
    assert 'Reliability design' not in legacy
    assert 'Target-cluster hazard bounds' not in legacy
    receipt['payload']['reliability'] = []
    _seal(receipt)
    rendered = render(receipt, 'Legacy')
    assert 'Reliability design' not in rendered
    assert _table(rendered, '### Method') == _table(legacy, '### Method')


def test_report_rejects_payload_tampering_instead_of_publishing_changed_totals():
    receipt = _receipt([_summary()])
    receipt['payload']['summary'][0]['successful'] = 1000
    with pytest.raises(ValueError, match='digest mismatch'):
        render(receipt, 'Corrupted results')


def test_report_rejects_scientific_tampering_even_when_outer_digest_is_updated():
    receipt = _receipt([_summary()])
    receipt['payload']['summary'][0]['successful'] = 1000
    receipt['payload_hash'] = canonical_hash(receipt['payload'])
    with pytest.raises(ValueError, match='Scientific content digest mismatch'):
        render(receipt, 'Resealed corrupt results')


def test_report_requires_a_complete_receipt_envelope():
    with pytest.raises(ValueError, match='receipt envelope'):
        render({'payload': _receipt([_summary()])['payload']}, 'Unwrapped payload')


def test_historical_report_checks_integrity_without_claiming_target_replay():
    receipt = _receipt([_summary()])
    before = deepcopy(receipt)
    rendered = render(receipt, 'Historical results')
    assert 'integrity-only' in rendered.lower()
    assert 'no target replay' in rendered.lower()
    assert 'authenticat' in rendered.lower()
    assert 'a' * 16 in rendered
    assert receipt == before


def test_fault_schedules_keep_type_onset_phase_and_symbol_strata_separate():
    schedules = [None,
                 {'type': 'sensor_drift', 'step': 0},
                 {'type': 'actuator_swap', 'step': 0},
                 {'type': 'sensor_drift', 'step': 1},
                 {'type': 'sensor_drift', 'step': 0, 'phase': 'calibration'},
                 {'type': 'sensor_drift', 'step': 0, 'phase': 'always'},
                 {'type': 'stuck_output', 'step': 0, 'value': 0},
                 {'type': 'stuck_output', 'step': 0, 'value': 1}]
    receipt = _receipt([_summary(fault_schedule=schedule) for schedule in schedules])
    before = deepcopy(receipt)
    rendered = render(receipt, 'Controlled faults')
    for heading in ('### Method', '### Per family'):
        records = _table(rendered, heading)
        assert len(records) == 8
        labels = {record['Conditions'].split('fault_schedule=', 1)[1] for record in records}
        assert labels == {'null',
                         '{"phase":"deployment","step":0,"type":"sensor_drift"}',
                         '{"phase":"deployment","step":0,"type":"actuator_swap"}',
                         '{"phase":"deployment","step":1,"type":"sensor_drift"}',
                         '{"phase":"calibration","step":0,"type":"sensor_drift"}',
                         '{"phase":"always","step":0,"type":"sensor_drift"}',
                         '{"phase":"deployment","step":0,"type":"stuck_output","value":0}',
                         '{"phase":"deployment","step":0,"type":"stuck_output","value":1}'}
    assert receipt == before


def test_effective_fault_defaults_pool_across_families_without_mutating_receipts():
    receipt = _receipt([
        _summary(fault_schedule={'type': 'sensor_drift', 'step': 0}),
        _summary('handshake', fault_schedule={'phase': 'deployment', 'step': 0,
                                             'type': 'sensor_drift'}),
        _summary(fault_schedule={'type': 'stuck_output', 'step': 1}),
        _summary('handshake', fault_schedule={'value': 0, 'phase': 'deployment',
                                             'step': 1, 'type': 'stuck_output'})])
    before = deepcopy(receipt)
    records = _table(render(receipt, 'Effective fault defaults'), '### Method')
    assert len(records) == 2
    assert all(record['Requests'] == '4' for record in records)
    assert any('"value":0' in record['Conditions'] for record in records)
    assert receipt == before


@pytest.mark.parametrize('schedules', [
    [None, {'type': 'sensor_drift', 'step': 0}],
    [{'type': 'sensor_drift', 'step': 0}, {'type': 'sensor_drift', 'step': 1}],
    [{'type': 'sensor_drift', 'step': 0},
     {'type': 'sensor_drift', 'step': 0, 'phase': 'calibration'}],
])
def test_legacy_summary_rejects_mixed_unrecorded_fault_conditions(schedules):
    receipt = _receipt([_summary()])
    receipt['payload']['rows'] = [
        {'parent_instance_id': f'p{index}', 'baseline': {}, 'configuration': {
            'family': 'latch', 'policy': 'task', 'admission': 'robust', 'budget': 16,
            'fault_schedule': schedule}}
        for index, schedule in enumerate(schedules)]
    _seal(receipt)
    with pytest.raises(ValueError, match='conditions'):
        render(receipt, 'Ambiguous legacy faults')


def test_legacy_summary_recovers_one_effective_fault_schedule_from_saved_rows():
    receipt = _receipt([_summary()])
    receipt['payload']['rows'] = [
        {'parent_instance_id': 'p', 'baseline': {}, 'configuration': {
            'family': 'latch', 'policy': 'task', 'admission': 'robust', 'budget': 16,
            'fault_schedule': schedule}}
        for schedule in ({'type': 'stuck_output', 'step': 1},
                         {'type': 'stuck_output', 'step': 1, 'phase': 'deployment', 'value': 0})]
    _seal(receipt)
    row = _table(render(receipt, 'Legacy fault defaults'), '### Per family')[0]
    assert 'fault_schedule={"phase":"deployment","step":1,"type":"stuck_output","value":0}' in row['Conditions']
    nominal = _table(render(_receipt([_summary()]), 'Legacy nominal'), '### Per family')[0]
    assert 'fault_schedule=null' in nominal['Conditions']


def test_legacy_condition_recovery_matches_effective_nested_fault_defaults():
    summary = _summary(fault_schedule={'type': 'stuck_output', 'step': 1})
    summary.pop('execution_mode')
    receipt = _receipt([summary])
    receipt['payload']['rows'][0]['configuration'] = {
        'family': 'latch', 'policy': 'task', 'admission': 'robust', 'budget': 16,
        'execution_mode': 'shielded',
        'fault_schedule': {'type': 'stuck_output', 'step': 1, 'phase': 'deployment', 'value': 0}}
    _seal(receipt)
    row = _table(render(receipt, 'Canonical legacy matching'), '### Per family')[0]
    assert 'execution_mode=shielded' in row['Conditions']
    assert 'fault_schedule={"phase":"deployment","step":1,"type":"stuck_output","value":0}' in row['Conditions']


def test_paired_reliability_and_fit_tables_keep_canonical_fault_conditions():
    schedule = {'type': 'stuck_output', 'step': 2, 'phase': 'calibration'}
    pair = {'contrast': 'entropy - fixed', 'budget': 16, 'parent_clusters': 2,
            'matched_cells': 4, 'mean_delta': 0.5, 'descriptive_95_interval': [0, 1],
            'fixed_admission': 'fit', 'families_pooled': ['latch'], 'fault_schedule': schedule}
    receipt = _receipt([_summary(method='task/fit', fault_schedule=schedule)], [pair])
    receipt['payload']['rows'][0].update(
        configuration={'family': 'latch', 'policy': 'task', 'admission': 'fit', 'budget': 16,
                       'implementation': 'procedural', 'seed': 17, 'fault_schedule': schedule},
        baseline={'fit_diagnostics': {'total_residual': 2, 'raw_mismatches': 1,
                                     'anchor_mismatches': 1, 'maps_tied_at_minimum': 3}},
        audit={'contract_satisfied': False})
    receipt['payload']['reliability'] = [_reliability(fault_schedule=schedule)]
    _seal(receipt)
    before = deepcopy(receipt)
    rendered = render(receipt, 'Fault conditions at every surface')
    label = 'fault_schedule={"phase":"calibration","step":2,"type":"stuck_output","value":0}'
    for heading in ('### Method', '### Per family', '### Paired',
                    '### Forced-fit', '### Reliability design'):
        assert all(label in row['Conditions'] for row in _table(rendered, heading))
    assert receipt == before
