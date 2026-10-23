"""Loopback workbench with a single cancellable scientific worker."""
from __future__ import annotations

from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import queue
import threading
from urllib.parse import urlsplit
import uuid

from . import __version__
from .fixtures import catalog
from .receipts import check_envelope, pack, replay, validate
from .study import ADMISSIONS, EXECUTION_MODES, POLICIES, Cancelled, RunConfig, run, run_study

MAX_BODY = 20 * 1024 * 1024


class Jobs:
    def __init__(self):
        self.jobs = {}
        self.lock = threading.RLock()
        self.queue = queue.Queue(maxsize=8)
        self.worker = threading.Thread(target=self._work, daemon=True, name='crosswire-science')
        self.worker.start()

    def submit(self, kind, configuration):
        with self.lock:
            if self.queue.full():
                raise ValueError('Worker queue is full; cancel or wait for an existing job')
            if len(self.jobs) >= 64:
                finished = next((k for k, v in self.jobs.items() if v['status'] in ('COMPLETE', 'FAILED', 'CANCELLED')), None)
                if finished:
                    del self.jobs[finished]
                else:
                    raise ValueError('Too many active jobs')
            identifier = uuid.uuid4().hex[:16]
            self.jobs[identifier] = {'id': identifier, 'status': 'QUEUED', 'kind': kind,
                                     'configuration': configuration, 'cancel': threading.Event(),
                                     'progress': {'current': 0, 'total': 1, 'message': 'Queued'}}
            self.queue.put_nowait(identifier)
        return {'id': identifier, 'status': 'QUEUED'}

    def snapshot(self, identifier):
        with self.lock:
            if identifier not in self.jobs:
                raise KeyError('Unknown job')
            value = self.jobs[identifier]
            return {k: v for k, v in value.items() if k not in ('cancel', 'configuration', 'kind')}

    def result(self, identifier):
        value = self.snapshot(identifier)
        if (value['status'] != 'COMPLETE'
                or value.get('result', {}).get('schema') not in ('crosswire-result-v1', 'crosswire-study-v1')):
            raise RuntimeError('Only completed experiment or study jobs have exportable evidence')
        return value['result']

    def cancel(self, identifier):
        with self.lock:
            if identifier not in self.jobs:
                raise KeyError('Unknown job')
            self.jobs[identifier]['cancel'].set()
        return self.snapshot(identifier)

    def import_result(self, receipt):
        # Envelope and digests are checked synchronously; the expensive exact
        # recomputation runs on the bounded, cancellable science worker.
        check_envelope(receipt)
        return self.submit('import', receipt)

    def replay_result(self, identifier):
        return self.submit('replay', pack(self.result(identifier)))

    def _work(self):
        while True:
            identifier = self.queue.get()
            if identifier is None:
                self.queue.task_done()
                return
            job = self.jobs[identifier]
            try:
                if job['cancel'].is_set():
                    raise Cancelled()
                with self.lock:
                    job['status'] = 'RUNNING'

                def progress(current, total, message):
                    with self.lock:
                        job['progress'] = {'current': current, 'total': total, 'message': message}

                if job['kind'] == 'run':
                    result = run(RunConfig.from_dict(job['configuration']), job['cancel'].is_set, progress)
                elif job['kind'] == 'study':
                    result = run_study(job['configuration'], job['cancel'].is_set, progress)
                elif job['kind'] == 'import':
                    result = validate(job['configuration'], job['cancel'].is_set, progress)
                elif job['kind'] == 'replay':
                    result = replay(job['configuration'], job['cancel'].is_set, progress)
                else:
                    raise ValueError('Unknown job kind')
                if job['cancel'].is_set():
                    raise Cancelled()
                done = {'import': 'Imported; exact scientific replay matched',
                        'replay': 'Replay complete'}.get(job['kind'], 'Scientific result complete')
                with self.lock:
                    job.update(status='COMPLETE', result=result,
                               progress={'current': 1, 'total': 1, 'message': done})
            except Cancelled:
                with self.lock:
                    job.update(status='CANCELLED', progress={'current': 0, 'total': 1, 'message': 'Cancelled; no complete receipt'})
            except Exception as exc:
                with self.lock:
                    job.update(status='FAILED', error=f'{type(exc).__name__}: {exc}')
            finally:
                self.queue.task_done()

    def close(self):
        with self.lock:
            for job in self.jobs.values():
                job['cancel'].set()
        try:
            self.queue.put(None, timeout=3)
        except queue.Full:
            return
        self.worker.join(5)


class Handler(BaseHTTPRequestHandler):
    server_version = 'CROSSWIRE/0.1'

    def log_message(self, *_):
        pass

    def _json(self, status, value):
        data = json.dumps(value, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _body(self):
        if self.headers.get_content_type() != 'application/json':
            raise ValueError('Expected application/json')
        length = int(self.headers.get('Content-Length', '0'))
        if not 0 < length <= MAX_BODY:
            raise ValueError('JSON request must be between 1 byte and 20 MiB')
        return json.loads(self.rfile.read(length), parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON number')))

    def _same_origin(self):
        host = self.headers.get('Host', '')
        expected = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        if host not in expected:
            return False
        origin = self.headers.get('Origin')
        return origin is None or origin in {f'http://{h}' for h in expected}

    def do_GET(self):
        if not self._same_origin():
            self._json(403, {'error': 'Only the local workbench origin is accepted'})
            return
        path = urlsplit(self.path).path
        try:
            if path == '/api/catalog':
                self._json(200, {'version': __version__, 'families': catalog(), 'policies': POLICIES,
                                 'admissions': ADMISSIONS, 'execution_modes': EXECUTION_MODES,
                                 'defaults': asdict(RunConfig())})
            elif path.startswith('/api/runs/'):
                parts = path.strip('/').split('/')
                if len(parts) == 3:
                    self._json(200, self.server.manager.snapshot(parts[2]))
                elif len(parts) == 4 and parts[3] == 'export':
                    self._json(200, pack(self.server.manager.result(parts[2])))
                else:
                    self._json(404, {'error': 'Unknown route'})
            elif path in ('/', '/index.html', '/styles.css', '/app.js'):
                name = 'index.html' if path == '/' else path[1:]
                data = (Path(__file__).parent / 'web' / name).read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', {'index.html': 'text/html', 'styles.css': 'text/css', 'app.js': 'text/javascript'}[name] + '; charset=utf-8')
                self.send_header('Content-Length', str(len(data)))
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
                self.end_headers()
                self.wfile.write(data)
            elif path == '/favicon.ico':
                self.send_response(204)
                self.send_header('Content-Length', '0')
                self.end_headers()
            else:
                self._json(404, {'error': 'Unknown route'})
        except KeyError as exc:
            self._json(404, {'error': str(exc)})
        except RuntimeError as exc:
            self._json(409, {'error': str(exc)})
        except (ValueError, TypeError) as exc:
            self._json(409, {'error': str(exc)})

    def do_POST(self):
        if not self._same_origin():
            self._json(403, {'error': 'Only the local workbench origin is accepted'})
            return
        path = urlsplit(self.path).path
        try:
            data = self._body()
            if path == '/api/runs':
                config = RunConfig.from_dict(data)
                self._json(202, self.server.manager.submit('run', asdict(config)))
            elif path == '/api/studies':
                # Full bounded study validation is performed before job dispatch.
                from .study import study_configs
                study_configs(data)
                self._json(202, self.server.manager.submit('study', data))
            elif path == '/api/import':
                if not isinstance(data, dict):
                    raise ValueError('Expected a receipt envelope')
                if 'receipt_text' in data:
                    receipt = json.loads(data['receipt_text'])
                elif 'receipt' in data:
                    receipt = data['receipt']
                else:
                    raise ValueError('Expected a receipt envelope')
                self._json(202, self.server.manager.import_result(receipt))
            elif path.startswith('/api/runs/'):
                parts = path.strip('/').split('/')
                if len(parts) == 4 and parts[3] == 'cancel':
                    self._json(200, self.server.manager.cancel(parts[2]))
                elif len(parts) == 4 and parts[3] == 'replay':
                    self._json(202, self.server.manager.replay_result(parts[2]))
                else:
                    self._json(404, {'error': 'Unknown route'})
            else:
                self._json(404, {'error': 'Unknown route'})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            self._json(400, {'error': str(exc)})
        except KeyError as exc:
            self._json(404, {'error': str(exc)})
        except RuntimeError as exc:
            self._json(409, {'error': str(exc)})


def make_server(port=8781):
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError('Invalid port')
    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.daemon_threads = True
    server.manager = Jobs()
    return server


def serve(port=8781, open_browser=False):
    server = make_server(port)
    url = f'http://127.0.0.1:{server.server_port}/'
    print(url, flush=True)
    if open_browser:
        import webbrowser
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        server.manager.close()
