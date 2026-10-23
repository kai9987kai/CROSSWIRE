"""Public prediction support is evidence of compatibility, never model inclusion."""
from copy import deepcopy
from itertools import product

from crosswire.certificates import check_result
from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.fixtures import evaluate_word, make_case, oracle_plan


def _result(family='latch', probes=None, *, temporal=False, escalate=False,
            anchors=None, admission='robust'):
    public = make_case(family, 17).public
    probes = probes or []
    anchors = anchors or {}
    space = CandidateSpace(Machine.from_dict(public['reference']),
                           Contract.from_dict(public['contract']), temporal)
    evidence = [{'word': p['word'][:len(p['outputs'])], 'outputs': p['outputs'],
                 'complete': True} for p in probes if p['outputs']]
    ids = space.survivors(evidence, anchors)
    decision = space.plan(ids, admission, transcripts=evidence, anchors=anchors)
    return {'schema': 'crosswire-result-v1',
            'configuration': {'admission': admission, 'temporal': temporal, 'escalate': escalate},
            'reference': public['reference'], 'contract': public['contract'],
            'anchors': anchors, 'target_id': 'public-test', 'probes': probes,
            'candidates': [space.adapters[i].to_dict() for i in ids], 'decision': decision}


def _diagnostics(result):
    checked = check_result(result)
    assert checked['valid'], checked['reason']
    assert 'model_diagnostics' in checked
    return checked['model_diagnostics']


def _probe(private, word):
    return {'word': list(word), 'outputs': evaluate_word(private, word)['outputs'], 'complete': True}


def test_no_observations_leaves_inclusion_unknown_even_when_admitted():
    result = _result('neutral')
    # A task decision and evidence for actual model inclusion are separate claims.
    assert result['decision']['admitted'] is True
    diagnostic = _diagnostics(result)
    assert diagnostic['inclusion_status'] == 'UNKNOWN'
    assert diagnostic['classes']['static']['candidate_count'] == 144
    assert diagnostic['classes']['static']['events'] == []
    assert diagnostic['classes']['static']['first_refutation'] is None
    assert diagnostic['reset_consistency']['status'] == 'UNKNOWN'


def test_forecasts_are_before_observations_and_do_not_change_with_future_evidence():
    first = {'word': [0, 1], 'outputs': [0, 1], 'complete': True}
    early = _diagnostics(_result(probes=[first]))['classes']['static']
    later = {'word': [1, 0], 'outputs': [3, 0], 'complete': True}
    full = _diagnostics(_result(probes=[first, later]))['classes']['static']
    assert full['events'][:2] == early['events']
    event = early['events'][0]
    assert event['survivors_before'] == 144
    assert event['predicted_output_counts'] == {'0': 36, '1': 36, '2': 36, '3': 36}
    assert event['survivors_after'] == 36
    assert event['prediction_status'] == 'SUPPORTED'


def test_reset_prefix_conflict_refutes_family_and_records_only_first_unsupported_event():
    probes = [{'word': [0, 1], 'outputs': [0, 1], 'complete': True},
              {'word': [0, 2, 1], 'outputs': [1, 0, 0], 'complete': True}]
    diagnostic = _diagnostics(_result(probes=probes))
    static = diagnostic['classes']['static']
    assert diagnostic['inclusion_status'] == 'REFUTED'
    first = static['first_refutation']
    assert (first['probe_index'], first['step'], first['word_prefix']) == (1, 1, [0])
    assert first['observed_output'] == 1
    assert first['predicted_output_counts'] == {'0': first['survivors_before']}
    assert first['survivors_before'] > 0
    assert first['survivors_after'] == 0
    assert static['events'][-1]['prediction_status'] == 'UNSCORED'
    assert static['unscored_symbols'] == 2
    reset = diagnostic['reset_consistency']
    assert reset['status'] == 'REFUTED'
    conflict = reset['first_conflict']
    assert conflict['word_prefix'] == [0]
    assert conflict['previous_probe_index'] == 0
    assert conflict['probe_index'] == 1


def test_enabled_temporal_envelope_survives_static_refutation():
    delayed = make_case('delay', 17)
    probes = [_probe(delayed.private, word) for word in product(range(3), repeat=2)]
    static = _diagnostics(_result('delay', probes))
    assert static['inclusion_status'] == 'REFUTED'
    enabled = _diagnostics(_result('delay', probes, escalate=True))
    assert enabled['enabled_classes'] == ['static', 'temporal']
    assert enabled['classes']['static']['inclusion_status'] == 'REFUTED'
    assert enabled['classes']['temporal']['candidate_count'] > 0
    assert enabled['inclusion_status'] == 'UNKNOWN'


def test_observed_prefix_of_failed_probe_is_scored_without_unexecuted_suffix():
    interrupted = {'word': [0, 1, 2], 'outputs': [0], 'complete': False}
    complete = {'word': [0], 'outputs': [0], 'complete': True}
    partial = _diagnostics(_result(probes=[interrupted]))
    short = _diagnostics(_result(probes=[complete]))
    assert partial == short
    assert partial['classes']['static']['scored_symbols'] == 1


def test_raw_equivalent_semantic_corruption_remains_unknown_with_explicit_blind_spot():
    case = make_case('semantic_corruption', 17)
    probes = [_probe(case.private, word) for word in product(range(3), repeat=3)]
    diagnostic = _diagnostics(_result('semantic_corruption', probes))
    assert diagnostic['inclusion_status'] == 'UNKNOWN'
    assert diagnostic['classes']['static']['candidate_count'] > 0
    assert any('semantic corruption' in warning.lower() for warning in diagnostic['blind_spots'])
    # The independent private instrument can observe harm despite raw compatibility.
    nominal = make_case('latch', 17)
    word = oracle_plan(nominal.private, 4)
    assert evaluate_word(case.private, word)['hazard'] is True


def test_extra_state_is_unknown_after_shallow_observations_until_longer_witness():
    case = make_case('extra_state', 17)
    probes = [_probe(case.private, word) for word in product(range(3), repeat=3)]
    assert _diagnostics(_result('extra_state', probes))['inclusion_status'] == 'UNKNOWN'
    nominal = make_case('long_trace', 17)
    witness = oracle_plan(nominal.private, 4)
    probes.append(_probe(case.private, witness))
    # The first long witness eliminates the nominal map, but a swapped advance/
    # reset interpretation still explains it. Refutation needs both witnesses.
    assert _diagnostics(_result('extra_state', probes))['inclusion_status'] == 'UNKNOWN'
    reset = case.private['input_map'].index(1)
    probes.append(_probe(case.private, [reset] * 4))
    diagnostic = _diagnostics(_result('extra_state', probes))
    assert diagnostic['inclusion_status'] == 'REFUTED'
    assert diagnostic['classes']['static']['first_refutation']['step'] == 4


def test_diagnostics_ignore_candidate_cache_and_untrusted_stored_certificate(monkeypatch):
    result = _result(probes=[{'word': [0], 'outputs': [0], 'complete': True}])
    expected = _diagnostics(result)
    result['evidence_certificate'] = {'model_diagnostics': {'inclusion_status': 'REFUTED'}}
    result['audit'] = {'secret': 'no diagnostics should read this'}
    monkeypatch.setattr(CandidateSpace, 'predict',
                        lambda *args: (_ for _ in ()).throw(AssertionError('cache used')))
    assert _diagnostics(result) == expected


def test_forced_fit_reports_refutation_independently_of_diagnostic_certificate_kind():
    probes = [{'word': [0], 'outputs': [0], 'complete': True},
              {'word': [0], 'outputs': [1], 'complete': True}]
    result = _result(probes=probes, admission='fit')
    checked = check_result(result)
    assert checked['kind'] == 'diagnostic'
    assert _diagnostics(result)['inclusion_status'] == 'REFUTED'


def test_conflicting_anchors_refute_before_any_observed_symbols():
    diagnostic = _diagnostics(_result(anchors={0: 1, 1: 1}))
    assert diagnostic['inclusion_status'] == 'REFUTED'
    first = diagnostic['classes']['static']['first_refutation']
    assert first['kind'] == 'anchor'
    assert first['raw'] == 1 and first['semantic'] == 1
    assert diagnostic['classes']['static']['events'] == []


def test_stored_model_diagnostics_cannot_change_the_public_certificate():
    result = _result()
    expected = _diagnostics(result)
    forged = deepcopy(result)
    forged['model_diagnostics'] = {'inclusion_status': 'REFUTED'}
    assert _diagnostics(forged) == expected


def test_nested_diagnostics_trace_each_live_model_once_per_observed_word(monkeypatch):
    import crosswire.certificates as certificates
    result = _result()
    machine = Machine.from_dict(result['reference'])
    original = certificates._trace
    calls = {}

    def counted_trace(reference, adapter, word):
        key = (adapter['id'], word)
        calls[key] = calls.get(key, 0) + 1
        return original(reference, adapter, word)

    monkeypatch.setattr(certificates, '_trace', counted_trace)
    certificates._model_diagnostics(machine, [], [((0, 1, 2), (0, 1, 2))], True)
    assert len(calls) == 720
    assert max(calls.values()) == 1
