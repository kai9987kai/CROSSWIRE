"""Bounded, counted JSON-lines access to one explicitly owned subprocess."""
import json
import math
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time


class InterfaceError(RuntimeError):
    def __init__(self, code, message=None):
        self.code = code
        super().__init__(message or code.replace('_', ' '))


class TargetProcess:
    def __init__(self, private, timeout=2.0):
        if isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or not math.isfinite(timeout) or timeout <= 0 or timeout > 30:
            raise ValueError('timeout must be finite and between zero and 30 seconds')
        self.timeout = timeout
        self.counts = dict(reset_attempts=0,step_attempts=0,reset_successes=0,step_successes=0,target_calls=0)
        self.last_trace = {'word':[],'outputs':[],'complete':False}
        self._sequence, self._closed = 0, False
        self._responses = queue.Queue()
        self._process = subprocess.Popen([sys.executable, '-m', 'crosswire.target_worker'],
            cwd=str(Path(__file__).resolve().parent.parent), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.pid = self._process.pid
        self._reader = threading.Thread(target=self._read, daemon=True)
        self._reader.start()
        try:
            self._request('init', config=private)
        except BaseException:
            self.close()
            raise

    def _read(self):
        try:
            while True:
                line = self._process.stdout.readline(65537)
                if not line:
                    self._responses.put(('error','worker_exit'))
                    return
                if len(line) > 65536 or not line.endswith(b'\n'):
                    self._responses.put(('error','malformed_response'))
                    return
                self._responses.put(('line',line))
        except (OSError, ValueError):
            self._responses.put(('error','worker_exit'))

    def _request(self, operation, **payload):
        try:
            if self._closed:
                raise InterfaceError('closed')
            self._sequence += 1
            message = {'id':self._sequence,'op':operation,**payload}
            encoded = (json.dumps(message,separators=(',',':'),allow_nan=False)+'\n').encode('utf-8')
            if len(encoded)>16384:
                raise InterfaceError('invalid_request')
            deadline = time.monotonic() + self.timeout
            written = queue.Queue(maxsize=1)
            def write():
                try:
                    self._process.stdin.write(encoded)
                    self._process.stdin.flush()
                    written.put(None)
                except (OSError,ValueError) as error:
                    written.put(error)
            threading.Thread(target=write,daemon=True).start()
            try:
                if written.get(timeout=self.timeout) is not None:
                    raise InterfaceError('worker_exit')
                kind, raw = self._responses.get(timeout=max(0,deadline-time.monotonic()))
            except queue.Empty:
                raise InterfaceError('timeout') from None
            if kind == 'error':
                raise InterfaceError(raw)
            try:
                response = json.loads(raw,parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
            except (ValueError,UnicodeError):
                raise InterfaceError('malformed_response') from None
            if not isinstance(response,dict) or type(response.get('id')) is not int or response['id'] != self._sequence:
                raise InterfaceError('malformed_response')
            if response.get('ok') is not True:
                raise InterfaceError('target_error')
            expected = {'id','ok','output'} if operation == 'step' else {'id','ok'}
            if set(response) != expected:
                raise InterfaceError('malformed_response')
            if operation == 'step':
                output = response['output']
                if type(output) is not int or not 0 <= output < 4:
                    raise InterfaceError('malformed_response')
                return output
            return None
        except InterfaceError:
            self.close()
            raise
        except (OSError,ValueError,TypeError):
            self.close()
            raise InterfaceError('worker_exit') from None

    def reset(self):
        self.counts['reset_attempts'] += 1
        self.counts['target_calls'] += 1
        self._request('reset')
        self.counts['reset_successes'] += 1

    def step(self, input):
        self.counts['step_attempts'] += 1
        self.counts['target_calls'] += 1
        if type(input) is not int or not 0 <= input < 3:
            self.close()
            raise InterfaceError('invalid_input')
        output = self._request('step',input=input)
        self.counts['step_successes'] += 1
        return output

    def query(self, word):
        self.last_trace = {'word':list(word),'outputs':[],'complete':False}
        try:
            self.reset()
            for symbol in self.last_trace['word']:
                self.last_trace['outputs'].append(self.step(symbol))
        except InterfaceError as error:
            error.trace = {'word':list(self.last_trace['word']),
                           'outputs':list(self.last_trace['outputs']),'complete':False}
            raise
        self.last_trace['complete'] = True
        return list(self.last_trace['outputs'])

    def close(self):
        if self._closed:
            return
        self._closed = True
        process = self._process
        if process.poll() is None:
            # Kill only this Popen object, never a name, process group or tree.
            process.terminate()
            try:
                process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=0.5)
        for pipe in (process.stdin,process.stdout):
            try:
                pipe.close()
            except OSError:
                pass
        if threading.current_thread() is not self._reader:
            self._reader.join(timeout=0.5)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

