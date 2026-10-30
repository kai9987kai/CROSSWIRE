"""Check a wheel in an isolated installation outside the source checkout.

Usage: python -I tools/check_distribution.py --wheel-dir dist
Uses only the standard library and the wheel being checked; installation never
uses an index or optional baseline dependencies.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import venv


_CHECKOUT_FINGERPRINT = r'''
import hashlib
import json
from pathlib import Path
import sys

checkout = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(checkout))
import crosswire
from crosswire.identity import source_hash

package = Path(crosswire.__file__).resolve().parent
if package != checkout / 'crosswire':
    raise RuntimeError('Checkout fingerprint imported a different CROSSWIRE package')
assets = {name: hashlib.sha256((package / 'web' / name).read_bytes()).hexdigest()
          for name in ('index.html', 'styles.css', 'app.js')}
print(json.dumps({'source_hash': source_hash(), 'web_assets': assets}))
'''


_INSTALLED_CHECK = r'''
import hashlib
import json
from pathlib import Path
import sys

environment = Path(sys.argv[1]).resolve()
expected = json.loads(sys.argv[2])
if not sys.flags.isolated or Path(sys.prefix).resolve() != environment:
    raise RuntimeError('Package check must use isolated Python from the temporary virtual environment')
import crosswire
from crosswire.identity import source_hash
from crosswire.receipts import pack, replay
from crosswire.study import RunConfig, run

package = Path(crosswire.__file__).resolve().parent
if not package.is_relative_to(environment):
    raise RuntimeError('CROSSWIRE import escaped the temporary virtual environment')
if source_hash() != expected['source_hash']:
    raise RuntimeError('Installed Python source hash differs from the checkout')
assets = {name: hashlib.sha256((package / 'web' / name).read_bytes()).hexdigest()
          for name in ('index.html', 'styles.css', 'app.js')}
if assets != expected['web_assets']:
    raise RuntimeError('Installed web asset hashes differ from the checkout')

# This zero-acquisition-budget fixture still deploys an observation-dependent
# policy, exercising the installed target-worker subprocess and private audit.
result = run(RunConfig(family='routing', budget=0, admission='adaptive',
                       execution_mode='shielded'))
if not result['decision']['admitted'] or result['audit']['contract_satisfied'] is not True:
    raise RuntimeError('Installed zero-budget adaptive deployment did not succeed')
if result['metrics']['target_calls'] != 0 or result['deployment']['target_calls'] <= 0:
    raise RuntimeError('Smoke run did not preserve zero acquisition calls and real deployment calls')
receipt = pack(result)
checked = replay(receipt)
if checked['valid'] is not True:
    raise RuntimeError('Installed scientific receipt did not replay exactly')
print(json.dumps({'package': str(package), 'isolated': bool(sys.flags.isolated),
                  'source_hash': source_hash(), 'web_assets': assets,
                  'acquisition_calls': result['metrics']['target_calls'],
                  'deployment_calls': result['deployment']['target_calls'],
                  'scientific_hash': result['scientific_hash'], 'replay_valid': True}))
'''


def _execute(command: list[str], directory: Path) -> str:
    completed = subprocess.run(command, cwd=directory, capture_output=True,
                               text=True, encoding='utf-8', timeout=180)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(f'Isolated package check failed ({completed.returncode}): {detail}')
    return completed.stdout


def check_distribution(wheel: Path, checkout: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix='crosswire-distribution-') as temporary:
        workspace = Path(temporary).resolve()
        if workspace.is_relative_to(checkout):
            raise RuntimeError('Temporary package-check directory must be outside the source checkout')
        working_directory = workspace / 'outside-checkout'
        working_directory.mkdir()
        environment = workspace / 'venv'
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
        fingerprint = _execute([sys.executable, '-I', '-c', _CHECKOUT_FINGERPRINT,
                                str(checkout)], working_directory)
        expected = json.loads(fingerprint)
        _execute([str(python), '-I', '-m', 'pip', '--isolated', 'install', '--no-index', '--no-deps',
                  '--disable-pip-version-check', str(wheel)], working_directory)
        output = _execute([str(python), '-I', '-c', _INSTALLED_CHECK, str(environment),
                           json.dumps(expected)], working_directory)
        return json.loads(output)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wheel-dir', type=Path, default=Path('dist'),
                        help='Directory containing exactly one wheel (default: dist)')
    args = parser.parse_args(argv)
    wheel_directory = args.wheel_dir.resolve()
    wheels = sorted(path for path in wheel_directory.glob('*.whl') if path.is_file()) if wheel_directory.is_dir() else []
    if len(wheels) != 1:
        parser.error(f'Expected exactly one wheel in {wheel_directory}; found {len(wheels)}')
    checkout = Path(__file__).resolve().parents[1]
    try:
        result = check_distribution(wheels[0], checkout)
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 1
    print(json.dumps({'wheel': str(wheels[0]), 'verification': result}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
