from copy import deepcopy
import pytest

from crosswire.study import RunConfig, run
from crosswire.receipts import pack, validate, replay, canonical_hash


def test_fresh_run_replays_scientific_content_without_timing_identity():
    result = run(RunConfig(family='latch', budget=4))
    receipt = pack(result)
    assert validate(receipt)['scientific_hash'] == result['scientific_hash']
    assert replay(receipt)['valid'] is True


def test_digest_alone_cannot_make_forged_decision_valid():
    receipt = pack(run(RunConfig(family='symmetric', budget=0)))
    forged = deepcopy(receipt)
    forged['payload']['decision']['admitted'] = True
    forged['payload_hash'] = canonical_hash(forged['payload'])
    with pytest.raises(ValueError):
        validate(forged)


def test_import_refuses_incomplete_or_source_mismatched_evidence():
    receipt = pack(run(RunConfig(family='latch', budget=0)))
    bad = deepcopy(receipt)
    bad['source_hash'] = '0' * 64
    with pytest.raises(ValueError):
        validate(bad)
    with pytest.raises(ValueError):
        validate({'schema': 'crosswire-receipt-v1', 'payload': {}})
