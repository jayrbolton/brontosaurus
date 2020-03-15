import multiprocessing
import requests
import json
import time
import os

from test.examples.paths import api

_PORT = 8081
_URL = f'http://0.0.0.0:{_PORT}'


def _wait_for_service():
    while True:
        try:
            requests.post(
                _URL,
                data=json.dumps({'method': 'hello'})
            ).raise_for_status()
            break
        except Exception:
            print('Waiting for API to start..')
            time.sleep(1)
    print('API started!')


def setup_module(module):
    kwargs = {'workers': 1, 'port': _PORT}
    proc = multiprocessing.Process(target=api.run, kwargs=kwargs, daemon=True)
    proc.start()
    _wait_for_service()


def test_valid_request1():
    """
    Basic happy path
    """
    resp = requests.post(
        _URL + '/subpath1',
        data=json.dumps({
            'id': 123,
            'jsonrpc': '2.0',
            'method': 'hello'
        })
    )
    assert resp.ok
    expected = '{"jsonrpc":"2.0","id":123,"result":"hello from subpath1"}'
    assert resp.text == expected


def test_valid_request2():
    """
    Basic happy path for subpath2
    """
    resp = requests.post(
        _URL + '/subpath2',
        data=json.dumps({
            'id': 123,
            'jsonrpc': '2.0',
            'method': 'hello'
        })
    )
    assert resp.ok
    expected = '{"jsonrpc":"2.0","id":123,"result":"hello from subpath2"}'
    assert resp.text == expected


def test_docs_paths():
    """
    Test that the API docs are at their proper paths.
    """
    assert os.path.exists('test/examples/docs/paths-root-api.md')
    assert os.path.exists('test/examples/docs/paths-subpath1.md')
    assert os.path.exists('test/examples/docs/paths-subpath1.md')
