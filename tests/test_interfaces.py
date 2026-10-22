import importlib
import time

import pytest


def api():
    assert importlib.util.find_spec('crosswire.interfaces') is not None, 'protocol implementation missing'
    return importlib.import_module('crosswire.interfaces')


def test_real_worker_queries_count_calls_and_reset_events():
    p = api()
    from crosswire.fixtures import make_case, evaluate_word
    case = make_case('latch')
    with p.TargetProcess(case.private) as process:
        assert process.query([0,1,2]) == evaluate_word(case.private,[0,1,2])['outputs']
        assert process.query([1]) == evaluate_word(case.private,[1])['outputs']
        assert process.counts == {'reset_attempts':2,'step_attempts':4,'reset_successes':2,'step_successes':4,'target_calls':6}
        assert process.last_trace == {'word':[1], 'outputs':evaluate_word(case.private,[1])['outputs'],'complete':True}
        owned = process._process
    assert owned.poll() is not None
    process.close()


@pytest.mark.parametrize('mode,code', [('malformed','malformed_response'),('timeout','timeout'),('exit','worker_exit')])
def test_faults_charge_failed_step_and_cleanup_exact_child(mode,code):
    p = api()
    from crosswire.fixtures import make_case
    process = p.TargetProcess(dict(make_case('malformed').private, fault_mode=mode))
    process.timeout = 0.15
    owned = process._process
    start = time.monotonic()
    with pytest.raises(p.InterfaceError) as error:
        process.query([0,1])
    assert error.value.code == code
    assert time.monotonic() - start < 2
    assert process.counts['reset_attempts'] == process.counts['reset_successes'] == 1
    assert process.counts['step_attempts'] == 1 and process.counts['step_successes'] == 0
    assert process.counts['target_calls'] == 2
    assert process.last_trace == {'word':[0,1],'outputs':[],'complete':False}
    assert owned.poll() is not None
    process.close()


def test_partial_trace_and_invalid_input_attempt():
    p = api()
    from crosswire.fixtures import make_case
    with p.TargetProcess(dict(make_case('malformed').private, fault_after=1)) as process:
        with pytest.raises(p.InterfaceError):
            process.query([0,1,2])
        assert len(process.last_trace['outputs']) == 1
        assert not process.last_trace['complete']
        assert process.counts['step_attempts'] == 2
    good = p.TargetProcess(make_case('latch').private)
    with pytest.raises(p.InterfaceError):
        good.step(True)
    assert good.counts['step_attempts'] == 1
    good.close()


def test_failed_query_attaches_raw_prefix_to_error():
    p = api()
    from crosswire.fixtures import make_case
    with p.TargetProcess(dict(make_case('malformed').private,fault_after=1)) as process:
        with pytest.raises(p.InterfaceError) as error:
            process.query([0,1])
        assert error.value.trace == process.last_trace
        assert len(error.value.trace['outputs']) == 1
        assert error.value.trace is not process.last_trace


def test_failed_reset_is_charged_without_any_step():
    p = api()
    from crosswire.fixtures import make_case
    with p.TargetProcess(dict(make_case('malformed').private,fault_operation='reset')) as process:
        with pytest.raises(p.InterfaceError):
            process.query([0])
        assert process.counts == {'reset_attempts':1,'step_attempts':0,'reset_successes':0,'step_successes':0,'target_calls':1}
