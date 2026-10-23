import json
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from crosswire.server import make_server


@pytest.fixture
def endpoint():
    server = make_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f'http://127.0.0.1:{server.server_port}'
    server.shutdown()
    server.server_close()
    server.manager.close()
    thread.join(3)


def send(base, path, data=None, headers=None):
    request = Request(base + path, data=json.dumps(data).encode() if data is not None else None,
                      headers={'Content-Type': 'application/json', **(headers or {})})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def completed(base, job):
    until = time.monotonic() + 25
    while time.monotonic() < until:
        value = send(base, '/api/runs/' + job['id'])
        if value['status'] in ('COMPLETE', 'FAILED', 'CANCELLED'):
            return value
        time.sleep(.05)
    raise AssertionError('Job did not finish')


def test_http_run_export_import_and_replay_use_real_worker(endpoint):
    cat = send(endpoint, '/api/catalog')
    assert 'task' in cat['policies']
    job = send(endpoint, '/api/runs', {'family': 'symmetric', 'budget': 0})
    value = completed(endpoint, job)
    assert value['status'] == 'COMPLETE'
    assert value['result']['decision']['admitted'] is False
    receipt = send(endpoint, f"/api/runs/{job['id']}/export")
    imported = send(endpoint, '/api/import', {'receipt': receipt})
    assert imported['status'] == 'QUEUED'
    assert completed(endpoint, imported)['result']['scientific_hash'] == value['result']['scientific_hash']
    replay_job = send(endpoint, f"/api/runs/{job['id']}/replay", {})
    assert replay_job['status'] == 'QUEUED'
    assert completed(endpoint, replay_job)['result']['valid'] is True


def test_api_rejects_invalid_configuration_and_cross_origin_mutation(endpoint):
    with pytest.raises(HTTPError) as exc:
        send(endpoint, '/api/runs', {'budget': True})
    assert exc.value.code == 400
    with pytest.raises(HTTPError) as exc:
        send(endpoint, '/api/runs', {}, {'Origin': 'https://unrelated.example'})
    assert exc.value.code == 403


def test_cancelled_study_cannot_be_exported_as_complete(endpoint):
    job = send(endpoint, '/api/studies', {'families': ['latch', 'handshake'], 'seeds': [17, 23, 29],
                                        'budgets': [8, 16], 'policies': ['task', 'fixed']})
    send(endpoint, f"/api/runs/{job['id']}/cancel", {})
    assert completed(endpoint, job)['status'] == 'CANCELLED'
    with pytest.raises(HTTPError) as exc:
        send(endpoint, f"/api/runs/{job['id']}/export")
    assert exc.value.code == 409


def test_static_server_cannot_read_source_or_parent_paths(endpoint):
    with urlopen(endpoint) as response:
        assert b'CROSSWIRE' in response.read()
    for path in ('/../pyproject.toml', '/crosswire/fixtures.py'):
        with pytest.raises(HTTPError) as exc:
            urlopen(endpoint + path)
        assert exc.value.code == 404


def test_replay_status_is_not_exportable_scientific_evidence(endpoint):
    job = send(endpoint, '/api/runs', {'family': 'symmetric', 'budget': 0})
    assert completed(endpoint, job)['status'] == 'COMPLETE'
    replay_job = send(endpoint, f"/api/runs/{job['id']}/replay", {})
    assert completed(endpoint, replay_job)['result']['valid'] is True
    with pytest.raises(HTTPError) as exc:
        send(endpoint, f"/api/runs/{replay_job['id']}/export")
    assert exc.value.code == 409
    assert 'evidence' in json.load(exc.value)['error'].lower()


def test_export_source_change_returns_json_conflict(endpoint, monkeypatch):
    job = send(endpoint, '/api/runs', {'family': 'symmetric', 'budget': 0})
    assert completed(endpoint, job)['status'] == 'COMPLETE'
    monkeypatch.setattr('crosswire.receipts.source_hash', lambda: 'changed-source')
    with pytest.raises(HTTPError) as exc:
        send(endpoint, f"/api/runs/{job['id']}/export")
    assert exc.value.code == 409
    assert 'source' in json.load(exc.value)['error'].lower()
