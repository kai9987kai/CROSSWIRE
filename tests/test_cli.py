import json
import subprocess
import sys

from crosswire import cli, receipts
from crosswire.study import RunConfig, run


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


def test_verify_recomputes_the_target_only_once(tmp_path, monkeypatch, capsys):
    path = tmp_path / 'case.json'
    path.write_text(json.dumps(receipts.pack(run(RunConfig(family='symmetric', budget=0)))), encoding='utf-8')
    calls = []
    real_replay = receipts.replay

    def counted(*args, **kwargs):
        calls.append(1)
        return real_replay(*args, **kwargs)

    monkeypatch.setattr(cli, 'replay', counted)
    monkeypatch.setattr(receipts, 'replay', counted)
    assert cli.main(['verify', str(path)]) == 0
    assert json.loads(capsys.readouterr().out)['valid'] is True
    assert len(calls) == 1


def test_check_independently_validates_public_model_evidence(tmp_path):
    path = tmp_path / 'case.json'
    path.write_text(json.dumps(receipts.pack(run(RunConfig(family='symmetric', budget=0)))), encoding='utf-8')
    checked = subprocess.run([sys.executable, '-m', 'crosswire', 'check', str(path)],
                             capture_output=True, text=True, timeout=30)
    assert checked.returncode == 0, checked.stderr
    assert json.loads(checked.stdout)['valid'] is True
