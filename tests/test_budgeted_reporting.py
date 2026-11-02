"""Saved reports preserve solver conditions even for legacy missing fields."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from crosswire.identity import canonical_hash, scientific_view
from crosswire.study import summarize
from tools.report import render


def receipt():
    root = Path(__file__).resolve().parents[1]
    value = json.loads((root / 'reports/resilience-workflows-receipt.json').read_text(encoding='utf-8'))
    rows = [deepcopy(value['payload']['rows'][0]) for _ in range(2)]
    for row, backend in zip(rows, ('flat', 'factored')):
        row['configuration']['candidate_backend'] = backend
    value['payload'].update(rows=rows, summary=summarize(rows), paired=[], reliability=[])
    return value


def seal(value):
    value['payload']['scientific_hash'] = canonical_hash(scientific_view(value['payload']))
    value['payload_hash'] = canonical_hash(value['payload'])
    return value


def test_report_keeps_backend_strata_and_saved_receipt_unchanged():
    value = seal(receipt())
    before = deepcopy(value)
    text = render(value, 'Backend conditions')
    assert 'candidate_backend=flat' in text
    assert 'candidate_backend=factored' in text
    section = text.split('### Method', 1)[1].split('### ', 1)[0]
    assert len([line for line in section.splitlines() if line.startswith('| in_family')]) == 2
    assert value == before


def test_legacy_report_refuses_unrecorded_mixed_backend_aggregate():
    value = receipt()
    value['payload']['summary'] = [deepcopy(value['payload']['summary'][0])]
    del value['payload']['summary'][0]['candidate_backend']
    with pytest.raises(ValueError, match='unrecorded conditions'):
        render(seal(value), 'Ambiguous backend aggregate')
