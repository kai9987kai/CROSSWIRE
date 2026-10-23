"""Private audit regressions for executed evidence and declared model scope."""
import pytest

from crosswire.audit import evaluate
from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.fixtures import evaluate_word, make_case


def audit_case(family='latch', *, temporal=False):
    case = make_case(family, seed=17, horizon=1)
    space = CandidateSpace(Machine.from_dict(case.public['reference']),
                           Contract.from_dict(case.public['contract']), temporal=temporal)
    return case, space


def test_completed_audit_reconstructs_executed_actions_instead_of_requested_plan():
    case, space = audit_case()
    inverse = {meaning: raw for raw, meaning in enumerate(case.private['input_map'])}
    requested = [inverse[0], inverse[1]]
    executed = [inverse[2]]
    observed = evaluate_word(case.private, executed)['outputs']
    result = evaluate(case, space, space.survivors([]),
                      {'admitted': True, 'word': requested}, [],
                      {'complete': True, 'executed_word': executed, 'outputs': observed})
    assert result['semantic_events'] == [2]
    assert result['hazard'] is True
    assert result['deployment_audit']['reconstruction_matches_observed'] is True


def test_calibration_audit_includes_hazard_in_successful_incomplete_probe_prefix():
    case, space = audit_case()
    inverse = {meaning: raw for raw, meaning in enumerate(case.private['input_map'])}
    prefix = [inverse[2]]
    probes = [{'word': prefix + [inverse[0]],
               'outputs': evaluate_word(case.private, prefix)['outputs'], 'complete': False}]
    result = evaluate(case, space, space.survivors([]),
                      {'admitted': False, 'word': None}, probes,
                      {'complete': False, 'outputs': []})
    assert result['calibration_hazardous_probes'] == 1


@pytest.mark.parametrize('family', ['routing', 'rotary', 'interlock'])
def test_catalog_in_family_mechanisms_receive_true_map_retention_audit(family):
    case, space = audit_case(family)
    result = evaluate(case, space, space.survivors([]),
                      {'admitted': False, 'word': None}, [],
                      {'complete': False, 'outputs': []})
    assert result['true_map_retained'] is True


def test_temporal_equivalence_scope_reports_actual_hypothesis_count():
    case, space = audit_case(temporal=True)
    result = evaluate(case, space, space.survivors([]),
                      {'admitted': False, 'word': None}, [],
                      {'complete': False, 'outputs': []})
    assert result['maps_checked'] == 720
    assert '720' in result['assumption_limits']
    assert 'temporal' in result['assumption_limits']
