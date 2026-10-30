"""Saved-content integrity does not establish replay or private-audit truth."""
from copy import deepcopy

import pytest

from crosswire import receipts
from crosswire.identity import canonical_hash, scientific_view


def _historical_receipt():
    payload = {'schema': 'crosswire-result-v1', 'source_hash': 'a' * 64,
               'configuration': {'family': 'latch', 'seed': 17, 'budget': 0},
               'decision': {'admitted': False}, 'audit': {'contract_satisfied': None},
               'metrics': {'target_calls': 0}}
    payload['scientific_hash'] = canonical_hash(scientific_view(payload))
    return {'schema': 'crosswire-receipt-v1', 'source_hash': 'a' * 64,
            'payload': payload, 'payload_hash': canonical_hash(payload)}


def test_integrity_accepts_historical_source_without_mutation():
    receipt = _historical_receipt()
    before = deepcopy(receipt)
    payload = receipts.check_integrity(receipt)
    assert payload['decision']['admitted'] is False
    assert payload['source_hash'] == 'a' * 64
    assert receipt == before


def test_integrity_rejects_changed_payload_even_with_well_formed_envelope():
    receipt = _historical_receipt()
    receipt['payload']['decision']['admitted'] = True
    with pytest.raises(ValueError, match='Receipt content digest mismatch'):
        receipts.check_integrity(receipt)


def test_integrity_checks_scientific_digest_after_outer_digest_is_resealed():
    receipt = _historical_receipt()
    receipt['payload']['decision']['admitted'] = True
    receipt['payload_hash'] = canonical_hash(receipt['payload'])
    with pytest.raises(ValueError, match='Scientific content digest mismatch'):
        receipts.check_integrity(receipt)


def test_integrity_rejects_conflicting_envelope_and_payload_source_identities():
    receipt = _historical_receipt()
    receipt['source_hash'] = 'b' * 64
    with pytest.raises(ValueError, match='source identity'):
        receipts.check_integrity(receipt)


@pytest.mark.parametrize('field,value', [('source_hash', ''), ('source_hash', None),
                                         ('source_hash', 'not-a-source-hash'),
                                         ('payload_hash', 'z' * 64)])
def test_integrity_requires_sha256_identities(field, value):
    receipt = _historical_receipt()
    receipt[field] = value
    with pytest.raises(ValueError):
        receipts.check_integrity(receipt)


@pytest.mark.parametrize('change', ['missing_envelope_field', 'wrong_envelope_schema',
                                   'nonobject_payload', 'wrong_payload_schema'])
def test_integrity_rejects_incomplete_or_unsupported_envelopes(change):
    receipt = _historical_receipt()
    if change == 'missing_envelope_field':
        receipt.pop('payload_hash')
    elif change == 'wrong_envelope_schema':
        receipt['schema'] = 'unrelated-receipt-v1'
    elif change == 'nonobject_payload':
        receipt['payload'] = []
        receipt['payload_hash'] = canonical_hash([])
    else:
        receipt['payload']['schema'] = 'unrelated-result-v1'
        receipt['payload_hash'] = canonical_hash(receipt['payload'])
    with pytest.raises(ValueError):
        receipts.check_integrity(receipt)


def test_integrity_does_not_relax_source_bound_import_and_replay():
    receipt = _historical_receipt()
    for operation in (receipts.check_envelope, receipts.validate, receipts.replay):
        with pytest.raises(ValueError, match='source revision'):
            operation(receipt)
