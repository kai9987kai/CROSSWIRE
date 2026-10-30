"""The standalone report command works without an editable installation."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

from crosswire.identity import canonical_hash, scientific_view


@pytest.mark.parametrize('tampered', [False, True])
def test_report_script_from_outside_checkout_checks_historical_integrity(tmp_path, tampered):
    payload = {'schema': 'crosswire-study-v1', 'source_hash': '1' * 64,
               'protocol_hash': canonical_hash({}), 'rows': [], 'summary': [], 'paired': []}
    payload['scientific_hash'] = canonical_hash(scientific_view(payload))
    receipt = {'schema': 'crosswire-receipt-v1', 'source_hash': payload['source_hash'],
               'payload': payload, 'payload_hash': '0' * 64 if tampered else canonical_hash(payload)}
    source = tmp_path / 'historical.json'
    source.write_text(json.dumps(receipt), encoding='utf-8')
    output = tmp_path / 'report.md'
    script = Path(__file__).resolve().parents[1] / 'tools' / 'report.py'
    completed = subprocess.run([sys.executable, '-I', str(script), str(source), '--out', str(output)],
                               cwd=tmp_path, capture_output=True, text=True, timeout=20)
    if tampered:
        assert completed.returncode != 0
        assert 'digest mismatch' in completed.stderr
        assert not output.exists()
    else:
        assert completed.returncode == 0, completed.stderr
        assert 'no target replay' in output.read_text(encoding='utf-8').lower()
