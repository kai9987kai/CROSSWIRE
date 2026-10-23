from copy import deepcopy

import pytest

from crosswire.core import CandidateSpace, Contract, Machine
from crosswire.fixtures import make_case


def public_result(family='latch', probes=None, temporal=False, anchors=None):
    public = make_case(family, 17).public
    space = CandidateSpace(Machine.from_dict(public['reference']), Contract.from_dict(public['contract']), temporal)
    probes = probes or []
    anchors = anchors or {}
    ids = space.survivors(probes, anchors)
    return {'schema': 'crosswire-result-v1', 'configuration': {'admission': 'robust', 'temporal': temporal},
            'reference': public['reference'], 'contract': public['contract'], 'anchors': anchors,
            'probes': probes, 'candidates': [space.adapters[i].to_dict() for i in ids],
            'decision': space.plan(ids), 'target_id': 'public-test'}, space


def test_checker_recomputes_all_survivors_and_rejects_omission():
    from crosswire.certificates import check_result
    result, _ = public_result()
    assert check_result(result)['valid'] is True
    result['candidates'].pop()
    result['decision']['candidate_count'] -= 1
    assert check_result(result)['valid'] is False


def test_checker_rejects_forged_admission_despite_claimed_certificate():
    from crosswire.certificates import check_result
    result, _ = public_result()
    result['decision'].update(admitted=True, word=[0], status='TASK_ADMISSIBLE')
    result['evidence_certificate'] = {'valid': True}
    assert check_result(result)['valid'] is False


def test_checker_is_independent_of_candidate_prediction_cache(monkeypatch):
    from crosswire.certificates import check_result
    result, _ = public_result('routing')
    from crosswire.adaptive import synthesize_policy
    space = CandidateSpace(Machine.from_dict(result['reference']), Contract.from_dict(result['contract']))
    result['decision'] = synthesize_policy(space, space.survivors([]))
    result['configuration']['admission'] = 'adaptive'
    monkeypatch.setattr(CandidateSpace, 'predict', lambda *args: (_ for _ in ()).throw(AssertionError('cache used')))
    checked = check_result(result)
    assert checked['valid'] is True
    assert checked['kind'] == 'admission'
    assert checked['checked_adapters'] == 144
    result['decision']['policy']['branches'].pop(next(iter(result['decision']['policy']['branches'])))
    assert check_result(result)['valid'] is False


def test_contradiction_core_rejects_whole_class_and_is_deletion_minimal():
    from crosswire.certificates import check_result
    # Same reset word cannot yield two different observations in a deterministic class.
    probes = [{'word': [0], 'outputs': [0], 'complete': True},
              {'word': [0], 'outputs': [1], 'complete': True},
              {'word': [0], 'outputs': [1], 'complete': True}]
    result, _ = public_result(probes=probes)
    checked = check_result(result)
    assert checked['valid'] is True
    assert checked['kind'] == 'contradiction'
    core = checked['contradiction_core']
    assert len(core) == 2
    assert checked['core_irreducible'] is True
    for item in core:
        remaining = [p for p in core if p != item]
        partial, _ = public_result(probes=[{'word': p['word'], 'outputs': p['outputs'], 'complete': True} for p in remaining])
        assert check_result(partial)['candidate_count'] > 0
    result['probes'] = probes[:1]
    assert check_result(result)['valid'] is False


def test_checker_includes_completed_prefix_of_failed_probe():
    from crosswire.certificates import check_result
    result, space = public_result(probes=[{'word': [0], 'outputs': [0], 'complete': True}])
    count = len(result['candidates'])
    assert count < 144
    result['probes'] = [{'word': [0, 1], 'outputs': [0], 'complete': False}]
    result['decision'].update(status='INTERFACE_ERROR', admitted=False, word=None)
    checked = check_result(result)
    assert checked['valid'] is True
    assert checked['candidate_count'] == count


def test_temporal_checker_enumerates_720_models():
    from crosswire.certificates import check_result
    result, _ = public_result(temporal=True)
    checked = check_result(result)
    assert checked['valid'] is True
    assert checked['checked_adapters'] == 720
    assert checked['candidate_count'] == 720


def test_checker_labels_point_estimate_as_diagnostic_not_safety_proof():
    from crosswire.certificates import check_result
    result, space = public_result()
    result['configuration']['admission'] = 'one_best'
    result['decision'] = space.plan(space.survivors([]), 'one_best')
    checked = check_result(result)
    assert checked['valid'] is True
    assert checked['kind'] == 'diagnostic'


@pytest.mark.parametrize('field,value', [('candidates', []), ('probes', [{'word': [False], 'outputs': [0], 'complete': True}]), ('anchors', {'99': 0})])
def test_malformed_public_evidence_fails_closed(field, value):
    from crosswire.certificates import check_result
    result, _ = public_result()
    result[field] = value
    assert check_result(result)['valid'] is False


def test_generated_run_has_checked_evidence_and_still_replays():
    from crosswire.certificates import check_result
    from crosswire.receipts import pack, replay
    from crosswire.study import RunConfig, run
    result = run(RunConfig(family='incompatible', budget=16, escalate=True))
    assert result['evidence_certificate']['kind'] == 'contradiction'
    assert result['evidence_certificate'] == check_result(result)
    assert replay(pack(result))['valid'] is True
