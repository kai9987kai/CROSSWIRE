import json
import subprocess
import sys


def test_cli_receipt_and_replay_survive_a_fresh_process(tmp_path):
    path = tmp_path / 'case.json'
    run = subprocess.run([sys.executable, '-m', 'crosswire', 'run', '--family', 'symmetric',
                          '--budget', '0', '--out', str(path)], capture_output=True, text=True, timeout=30)
    assert run.returncode == 0, run.stderr
    data = json.loads(path.read_text())
    assert data['payload']['decision']['admitted'] is False
    check = subprocess.run([sys.executable, '-m', 'crosswire', 'replay', str(path)],
                            capture_output=True, text=True, timeout=30)
    assert check.returncode == 0, check.stderr
    assert 'true' in check.stdout.lower()
