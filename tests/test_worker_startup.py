"""Interpreter startup and target response deadlines are different boundaries."""
import subprocess
import sys

import pytest

from crosswire import interfaces


def test_slow_startup_has_its_own_bound_without_weakening_counted_reset_deadline(monkeypatch):
    real_popen = subprocess.Popen
    script = (
        'import json,sys,time\n'
        'for line in sys.stdin:\n'
        ' r=json.loads(line)\n'
        ' time.sleep(0.2)\n'
        ' print(json.dumps({"id":r["id"],"ok":True}),flush=True)\n'
    )
    def launch(command, **kwargs):
        return real_popen([sys.executable, '-u', '-c', script], **kwargs)
    monkeypatch.setattr(interfaces.subprocess, 'Popen', launch)
    process = interfaces.TargetProcess({}, timeout=0.05)
    assert process.startup_timeout == 10
    owned = process._process
    with pytest.raises(interfaces.InterfaceError, match='timeout'):
        process.reset()
    assert process.counts['reset_attempts'] == process.counts['target_calls'] == 1
    assert process.counts['reset_successes'] == process.counts['step_attempts'] == 0
    assert owned.poll() is not None


@pytest.mark.parametrize('value', [True, 0, -1, 31, float('inf'), float('nan')])
def test_startup_deadline_is_finite_positive_and_bounded(value):
    with pytest.raises(ValueError, match='startup_timeout'):
        interfaces.TargetProcess({}, startup_timeout=value)
