"""Private target process. Standard output contains protocol JSON exclusively."""
import json
import os
import sys
import time

from .fixtures import make_engine


def _send(message):
    sys.stdout.write(json.dumps(message,separators=(',',':'),allow_nan=False)+'\n')
    sys.stdout.flush()


def main():
    engine, config, steps = None, None, 0
    try:
        for line in sys.stdin:
            request_id = None
            try:
                if len(line)>16384:
                    raise ValueError('request too large')
                request = json.loads(line)
                if not isinstance(request,dict) or type(request.get('id')) is not int:
                    raise ValueError('invalid envelope')
                request_id, operation = request['id'], request.get('op')
                if operation == 'init' and engine is None and set(request)=={'id','op','config'}:
                    config = request['config']
                    engine = make_engine(config)
                elif operation == 'reset' and engine is not None and set(request)=={'id','op'}:
                    if config['family']=='malformed' and config.get('fault_operation')=='reset':
                        sys.stdout.write('{malformed\n')
                        sys.stdout.flush()
                        continue
                    engine.reset()
                    steps = 0
                elif operation == 'step' and engine is not None and set(request)=={'id','op','input'}:
                    if config['family']=='malformed' and steps >= config.get('fault_after',0):
                        mode = config.get('fault_mode','malformed')
                        if mode == 'timeout':
                            time.sleep(60)
                        if mode == 'exit':
                            os._exit(3)
                        sys.stdout.write('{malformed\n')
                        sys.stdout.flush()
                        continue
                    output = engine.step(request['input'])
                    steps += 1
                    _send({'id':request_id,'ok':True,'output':output})
                    continue
                elif operation == 'close' and set(request)=={'id','op'}:
                    _send({'id':request_id,'ok':True})
                    return
                else:
                    raise ValueError('invalid operation')
                _send({'id':request_id,'ok':True})
            except (ValueError,KeyError,TypeError,IndexError):
                _send({'id':request_id,'ok':False,'error':'invalid_request'})
    finally:
        if engine is not None:
            engine.close()


if __name__ == '__main__':
    main()
