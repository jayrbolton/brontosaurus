import multiprocessing
from brontosaurus import API, logger
import requests
import json
import time
from uuid import uuid4

_URL = 'http://localhost:8080'
_URL_CORS = 'http://localhost:8088'

desc = """
This is a server for running tests on brontosaurus.
"""

api = API('Test Server', desc)

message = {
    '$id': '#message',
    'title': 'Message',
    'description': 'Echo message object.',
    'type': 'object',
    'required': ['message'],
    'properties': {
        'message': {
            'title': 'Message',
            'description': 'String to echo back to you',
            'type': 'string'
        }
    }
}


@api.method('echo', 'Is there an echo in here?')
@api.params(message)
@api.result(message)
def echo(params, headers):
    logger.debug('This is a log message from the echo method.')
    return {'message': params['message'] * 10}


@api.method('invalid_result', 'Test a result that fails schema check')
@api.params(message)
@api.result(message)
def invalid_result(params, headers):
    return {'xyz': 123}


@api.method('require_header', 'Test the header decorator')
@api.require_header('custom', r'xyz[0-9]+')
def header_format(params, headers):
    return headers['custom']


def _wait_for_service():
    while True:
        try:
            requests.post(
                _URL,
                data=json.dumps({'method': 'echo', 'params': {'message': 'x'}})
            ).raise_for_status()
            requests.post(
                _URL_CORS,
                data=json.dumps({'method': 'echo', 'params': {'message': 'x'}})
            ).raise_for_status()
            break
        except Exception:
            print('Waiting for API to start..')
            time.sleep(1)
    print('API started!')


def setup_module(module):
    kwargs = {'workers': 1, 'port': 8080}
    proc = multiprocessing.Process(target=api.run, kwargs=kwargs, daemon=True)
    proc.start()
    kwargs_cors = {'workers': 1, 'cors': True, 'port': 8088}
    proc_cors = multiprocessing.Process(target=api.run, kwargs=kwargs_cors, daemon=True)
    proc_cors.start()
    _wait_for_service()


def test_valid_request():
    """
    Basic happy path
    """
    req_id = str(uuid4())
    resp = requests.post(
        _URL,
        data=json.dumps({
            'id': req_id,
            'jsonrpc': '2.0',
            'method': 'echo',
            'params': {
                'message': 'hi'
            }
        })
    )
    assert resp.ok, resp.text
    expected = {"jsonrpc": "2.0", "id": req_id, "result": {"message": "hihihihihihihihihihi"}}
    assert resp.json() == expected


def test_options_request():
    resp = requests.options(_URL)
    assert resp.ok, resp.text
    assert resp.text == ''
    assert resp.status_code == 204


def test_path_not_found():
    body = {'id': 0, 'jsonrpc': '2.0', 'method': 'echo', 'params': {}}
    resp = requests.post(_URL + '/what', data=json.dumps(body))
    assert not resp.ok, resp.text
    assert resp.status_code == 404
    assert resp.text == 'null'


def test_invalid_json_syntax():
    resp = requests.post(
        _URL,
        data='!!!'
    )
    assert not resp.ok, resp.text
    assert resp.status_code == 400
    expected = {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": -32700,
            "message": "Failed when parsing body as json"
        }
    }
    assert resp.json() == expected


def test_missing_method_field():
    resp = requests.post(
        _URL,
        data='{}'
    )
    assert not resp.ok, resp.text
    assert resp.status_code == 400
    expected = {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": -32600,
            "message": "Invalid JSON RPC 2.0 request",
            "data": {
                "validation_error": "'method' is a required property",
                "value": {},
                "path": []
            }
        }
    }
    assert resp.json() == expected


def test_missing_params():
    resp = requests.post(
        _URL,
        data='{"method": "echo"}'
    )
    assert not resp.ok, resp.text
    assert resp.status_code == 400
    expected = {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": -32602,
            "error": "Missing params"
        }
    }
    assert resp.json() == expected


def test_unknown_method():
    resp = requests.post(
        _URL,
        data='{"method": "xyz"}'
    )
    assert not resp.ok, resp.text
    assert resp.status_code == 400
    expected = {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": -32601,
            "message": "Unknown method: 'xyz'"
        }
    }
    assert resp.json() == expected


def test_invalid_jsonrpc_type():
    """
    Invalid value for the "jsonrpc" field in the request.
    """
    resp = requests.post(
        _URL,
        data='{"jsonrpc": 123, "method": "echo"}'
    )
    assert not resp.ok, resp.text
    assert resp.status_code == 400
    expected = {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": -32600,
            "message": "Invalid JSON RPC 2.0 request",
            "data": {
                "validation_error": "'2.0' was expected",
                "value": 123,
                "path": [
                    "jsonrpc"
                ]
            }
        }
    }
    assert resp.json() == expected


def test_invalid_id_type():
    """
    Invalid value for the "id" field in the request.
    """
    resp = requests.post(
        _URL,
        data='{"id": {}, "method": "echo"}'
    )
    assert not resp.ok, resp.text
    assert resp.status_code == 400
    expected = {
        "jsonrpc": "2.0",
        "id": {},
        "error": {
            "code": -32600,
            "message": "Invalid JSON RPC 2.0 request",
            "data": {
                "validation_error": "{} is not of type 'integer', 'string', 'number', 'null'",
                "value": {},
                "path": [
                    "id"
                ]
            }
        }
    }
    assert resp.json() == expected


def test_invalid_params():
    """
    Test a params schema validation failure
    """
    resp = requests.post(
        _URL,
        data='{"method": "echo", "params": {"message": 123}}'
    )
    assert not resp.ok, resp.text
    assert resp.status_code == 400
    expected = {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": -32602,
            "message": "123 is not of type 'string'",
            "data": {
                "failed_validator": "type",
                "value": 123,
                "path": [
                    "message"
                ]
            }
        }
    }
    assert resp.json() == expected


def test_invalid_result():
    """
    Test a schema failure for a result
    """
    resp = requests.post(
        _URL,
        data='{"method": "invalid_result", "params": {"message": "hi"}}'
    )
    assert not resp.ok, resp.text
    assert resp.status_code == 500


def test_no_cors():
    resp = requests.post(
        _URL,
        data=json.dumps({
            'id': 123,
            'jsonrpc': '2.0',
            'method': 'echo',
            'params': {
                'message': 'hi'
            }
        })
    )
    assert resp.ok, resp.text
    expected = {
        "jsonrpc": "2.0",
        "id": 123,
        "result": {
            "message": "hihihihihihihihihihi"
        }
    }
    assert resp.json() == expected


def test_valid_bulk_request():
    """
    Basic happy path for a bulk request
    """
    resp = requests.post(
        _URL,
        data=json.dumps([{
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'echo',
            'params': {
                'message': 'hi'
            }
        }, {
            'id': 2,
            'jsonrpc': '2.0',
            'method': 'echo',
            'params': {
                'message': 'bye'
            }
        }])
    )
    assert resp.ok, resp.text
    expected = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "message": "hihihihihihihihihihi"
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "message": "byebyebyebyebyebyebyebyebyebye"
            }
        }
    ]
    assert resp.json() == expected


def test_header_validation_valid():
    resp = requests.post(
        _URL,
        data=json.dumps({
            'method': 'require_header'
        }),
        headers={'custom': 'xyz123'}
    )
    assert resp.ok, resp.text
    assert resp.json() == {'jsonrpc': '2.0', 'id': None, 'result': 'xyz123'}


def test_header_validation_invalid_req():
    resp = requests.post(
        _URL,
        data=json.dumps({
            'method': 'require_header'
        }),
        headers={'custom': 'xyz'}
    )
    assert not resp.ok, resp.text
    err = resp.json()['error']
    assert err['code'] == -32602
    assert err['error'] == "Header with key 'custom' does not match the format 'xyz[0-9]+'."


def test_header_validation_missing_key():
    resp = requests.post(
        _URL,
        data=json.dumps({
            'method': 'require_header'
        }),
        headers={}
    )
    assert not resp.ok, resp.text
    err = resp.json()['error']
    assert err['code'] == -32602
    assert err['error'] == "Header with key 'custom' required but not provided."


def test_no_cors_default_headers():
    req_id = str(uuid4())
    resp = requests.post(
        _URL,
        data=json.dumps({
            'id': req_id,
            'jsonrpc': '2.0',
            'method': 'echo',
            'params': {
                'message': 'hi'
            }
        })
    )
    expected = {
        'Connection': 'keep-alive',
        'Keep-Alive': '5',
        'Content-Length': '105',
        'Content-Type': 'application/json'
    }
    assert resp.headers == expected


def test_cors_headers():
    req_id = str(uuid4())
    resp = requests.post(
        _URL_CORS,
        data=json.dumps({
            'id': req_id,
            'jsonrpc': '2.0',
            'method': 'echo',
            'params': {
                'message': 'hi'
            }
        })
    )
    expected = {
        'Connection': 'keep-alive',
        'Keep-Alive': '5',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': '*',
        'Content-Length': '105',
        'Content-Type': 'application/json'
    }
    assert resp.headers == expected
