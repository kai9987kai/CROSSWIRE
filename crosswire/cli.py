"""Command line entry points share the browser's exact scientific runtime."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys

from .study import ADMISSIONS, POLICIES, RunConfig, run, run_study
from .fixtures import catalog
from .receipts import pack, replay, validate


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    os.replace(temp, path)


def main(argv=None):
    parser = argparse.ArgumentParser(prog='crosswire', description='Finite behavioral interoperability laboratory')
    commands = parser.add_subparsers(dest='command', required=True)
    one = commands.add_parser('run')
    defaults = asdict(RunConfig())
    for name in ('family', 'implementation', 'split', 'policy', 'admission'):
        choices = {'family': [f['id'] for f in catalog()], 'implementation': ['table', 'procedural'],
                   'split': ['development', 'evaluation'], 'policy': POLICIES, 'admission': ADMISSIONS}[name]
        one.add_argument('--' + name, default=defaults[name], choices=choices)
    for name in ('seed', 'budget', 'horizon'):
        one.add_argument('--' + name, default=defaults[name], type=int)
    one.add_argument('--anchors', action='store_true')
    one.add_argument('--out', type=Path)
    study = commands.add_parser('study')
    study.add_argument('--config', type=Path, required=True)
    study.add_argument('--out', type=Path, required=True)
    for name in ('verify', 'replay'):
        commands.add_parser(name).add_argument('receipt', type=Path)
    server = commands.add_parser('serve')
    server.add_argument('--port', type=int, default=8781)
    server.add_argument('--open', action='store_true')
    commands.add_parser('catalog')
    args = parser.parse_args(argv)
    try:
        if args.command == 'serve':
            from .server import serve
            serve(args.port, args.open)
            return 0
        if args.command == 'catalog':
            print(json.dumps(catalog(), indent=2))
            return 0
        if args.command == 'run':
            cfg = {name: getattr(args, name) for name in defaults}
            result = run(RunConfig.from_dict(cfg))
            receipt = pack(result)
            if args.out:
                _write(args.out, receipt)
                print(json.dumps({'path': str(args.out.resolve()), 'decision': result['decision'],
                                  'contract_satisfied': result['audit']['contract_satisfied'],
                                  'scientific_hash': result['scientific_hash']}))
            else:
                print(json.dumps(receipt, indent=2))
        elif args.command == 'study':
            spec = json.loads(args.config.read_text(encoding='utf-8'))
            result = run_study(spec)
            _write(args.out, pack(result))
            print(json.dumps({'path': str(args.out.resolve()), 'runs': len(result['rows']),
                              'summary': result['summary'], 'paired': result['paired']}))
        else:
            receipt = json.loads(args.receipt.read_text(encoding='utf-8'))
            checked = replay(receipt)
            if args.command == 'verify':
                validate(receipt)
            print(json.dumps(checked))
            return 0 if checked['valid'] else 1
        return 0
    except (ValueError, TypeError, OSError, RuntimeError, ImportError) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        return 1
