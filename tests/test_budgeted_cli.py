"""Backend and experiment policy plumbing without executing changing science."""
import json
import threading
from urllib.request import urlopen

import pytest

from crosswire import cli
from crosswire.server import make_server


def _capture_configuration(monkeypatch):
    configurations = []

    def capture(configuration):
        configuration.check()
        configurations.append(configuration)
        return {'decision': {'admitted': False}, 'audit': {'contract_satisfied': None},
                'scientific_hash': 'configuration-only'}

    monkeypatch.setattr(cli, 'run', capture)
    monkeypatch.setattr(cli, 'pack', lambda result: result)
    return configurations


@pytest.mark.parametrize('flag,backend', [('--candidate-backend', 'factored'),
                                          ('--candidate_backend', 'flat')])
def test_cli_routes_selected_backend_and_lookahead_policy(flag, backend, tmp_path, monkeypatch, capsys):
    configurations = _capture_configuration(monkeypatch)
    output = tmp_path / 'configuration.json'
    assert cli.main(['run', flag, backend, '--policy', 'lookahead', '--budget', '4',
                     '--out', str(output)]) == 0
    assert len(configurations) == 1
    assert configurations[0].candidate_backend == backend
    assert configurations[0].policy == 'lookahead'
    assert configurations[0].budget == 4
    assert json.loads(capsys.readouterr().out)['path'] == str(output.resolve())


def test_cli_preserves_flat_backend_for_omitted_selection(monkeypatch, capsys):
    configurations = _capture_configuration(monkeypatch)
    assert cli.main(['run', '--budget', '0']) == 0
    assert configurations[0].candidate_backend == 'flat'
    capsys.readouterr()


def test_cli_rejects_unknown_backend_before_dispatch(monkeypatch, capsys):
    configurations = _capture_configuration(monkeypatch)
    with pytest.raises(SystemExit) as stopped:
        cli.main(['run', '--candidate-backend', 'approximate'])
    assert stopped.value.code == 2
    assert configurations == []
    assert 'invalid choice' in capsys.readouterr().err


def test_catalog_exposes_backend_choices_policy_and_nominal_default():
    server = make_server(port=0)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        with urlopen(f'http://127.0.0.1:{server.server_port}/api/catalog', timeout=10) as response:
            catalog = json.load(response)
        assert catalog['candidate_backends'] == ['flat', 'factored']
        assert catalog['defaults']['candidate_backend'] == 'flat'
        assert 'lookahead' in catalog['policies']
    finally:
        server.shutdown()
        server.server_close()
        server.manager.close()
        worker.join(3)
