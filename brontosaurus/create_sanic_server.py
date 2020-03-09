"""
Generate the sanic server object from a brontosaurus API object.
"""
import sanic
from sanic.log import error_logger
import jsonschema.exceptions
import traceback
import threading
import multiprocessing
import re
import sys
import os


def _init_log_config(development, log_path):
    level = "DEBUG" if development else "WARNING"
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            "sanic.root": {
                "level": level,
                "handlers": ["console", "rot_file"]
            },
            "sanic.error": {
                "level": level,
                "handlers": ["error_console", "rot_file"],
                "propagate": True,
                "qualname": "sanic.error",
            },
            "sanic.access": {
                "level": level,
                "handlers": ["access_console", "rot_file_access"],
                "propagate": True,
                "qualname": "sanic.access",
            },
        },
        'handlers': {
            "rot_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "generic",
                "filename": log_path,
                "maxBytes": 1048576,
                "backupCount": 3
            },
            "rot_file_access": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "access",
                "filename": log_path,
                "maxBytes": 1048576,
                "backupCount": 3
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": sys.stdout,
            },
            "error_console": {
                "class": "logging.StreamHandler",
                "formatter": "generic",
                "stream": sys.stderr,
            },
            "access_console": {
                "class": "logging.StreamHandler",
                "formatter": "access",
                "stream": sys.stdout,
            },
        },
        'formatters': {
            "generic": {
                "format": "%(asctime)s %(levelname)-8s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "class": "logging.Formatter",
            },
            "access": {
                "format": "%(asctime)s %(levelname)-8s %(host)s %(request)s %(message)s-> %(status)d",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "class": "logging.Formatter",
            },
        },
    }


def create_sanic_server(api, workers, cors, development, log_path=None):
    if not log_path:
        log_path = os.path.join('tmp', 'app.log')
        os.makedirs('tmp', exist_ok=True)
    app = sanic.Sanic(strict_slashes=False, log_config=_init_log_config(development, log_path))
    methods = ['OPTIONS', 'PUT', 'POST', 'GET', 'DELETE']

    @app.route("/", methods=methods)
    @app.route("/<subpath:path>", methods=methods)
    def root(req, subpath=None):
        if req.method == 'OPTIONS':
            return sanic.response.raw(b'')
        try:
            req_json = req.json
        except sanic.exceptions.InvalidUsage as err:
            return sanic.response.json(_invalid_json_resp(req, err), 400)
        if isinstance(req_json, list):
            # Handle a bulk request
            responses = []
            threads = []
            resp_queue = multiprocessing.Queue()
            for each in req_json:
                args = (api, req, each, development, resp_queue, subpath)
                thread = threading.Thread(target=_handle_root_resp_async, args=args, daemon=True)
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
            while resp_queue.qsize():
                resp = resp_queue.get()
                responses.append(resp)
            return sanic.response.json(responses, 200)
        else:
            # Handle a single request
            (resp, code) = _handle_root_resp(api, req, req_json, development, subpath)
            return sanic.response.json(resp, code)

    # Handle an OPTIONS request
    @app.middleware('request')
    async def cors_options(request):
        if request.method == 'OPTIONS':
            return sanic.response.raw(b'', status=204)

    # Handle a 404
    @app.exception(sanic.exceptions.NotFound)
    def not_found(req, err):
        return sanic.response.raw(b'', 404)

    @app.exception(Exception)
    def unknown_error(req, err):
        error_logger.error(err)
        error_logger.error(traceback.format_exc())
        return sanic.response.raw(b'', 500)

    if cors:
        # Handle cors response headers
        @app.middleware('response')
        async def cors_resp(req, res):
            res.headers['Access-Control-Allow-Origin'] = '*'
            res.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            res.headers['Access-Control-Allow-Headers'] = '*'
    return app


def _handle_root_resp(api, req, req_json, development, path):
    """
    Returns the JSON body of the response and the HTTP status code in a pair.
    """
    try:
        jsonschema.validate(req_json, json_rpc2_schema)
    except jsonschema.exceptions.ValidationError as err:
        error_logger.debug(err)
        return (_invalid_json_rpc_resp(req_json, err), 400)
    headers = dict(req.headers)
    meth_name = req_json['method']
    if path:
        print('HAS PATH', path)
        if path not in api.subpaths:
            return (sanic.response.raw(b''), 404)
        api_handler = api.subpaths[path]
    else:
        api_handler = api
    if meth_name not in api_handler.method_names:
        return (_unknown_method_resp(req_json, meth_name), 400)
    meth_id = api_handler.method_names[meth_name]
    meth = api_handler.methods[meth_id]
    # Validate the headers
    if 'headers' in meth:
        for (key, pattern) in meth['headers']:
            if key not in headers:
                return (_missing_header_resp(req_json, key), 400)
            if not re.match(pattern, headers[key]):
                return (_invalid_header_resp(req_json, key, pattern), 400)
    # Validate the parameters
    if 'params_schema' in meth:
        if req_json.get('params') is None:
            return (_missing_params_resp(req_json), 400)
        try:
            jsonschema.validate(req_json.get('params'), meth['params_schema'])
        except jsonschema.exceptions.ValidationError as err:
            return (_invalid_params_resp(req_json, err), 400)
    # Compute the result
    func = meth['func']
    try:
        result = func(req_json.get('params'), headers)
    except Exception as err:
        return (_server_err_resp(req_json, err), 500)
    # Validate the result
    if development and 'result_schema' in meth:
        jsonschema.validate(result, meth['result_schema'])
    return ({
        'jsonrpc': '2.0',
        'id': _get_req_id(req_json),
        'result': result
    }, 200)


def _handle_root_resp_async(api, req, req_json, development, resp_queue, path):
    (resp, status) = _handle_root_resp(api, req, req_json, development, path)
    resp_queue.put(resp)


# A forgiving JSON Schema for JSON RPC 2.0. Does not require the "jsonrpc" or
# "id" fields.
json_rpc2_schema = {
    'type': 'object',
    'required': ['method'],
    'properties': {
        'method': {
            'type': 'string'
        },
        'id': {
            'type': ['integer', 'string', 'number', 'null']
        },
        'params': {
            'type': ['array', 'object']
        },
        'jsonrpc': {
            'const': '2.0'
        }
    }
}


def _unknown_method_resp(req_json, meth_name):
    return {
        'jsonrpc': '2.0',
        'id': _get_req_id(req_json),
        'error': {
            'code': -32601,
            'message': f"Unknown method: '{meth_name}'"
        }
    }


def _invalid_json_resp(req, err):
    return {
        'jsonrpc': '2.0',
        'id': None,
        'error': {
            'code': -32700,
            'message': str(err)
        }
    }


def _invalid_json_rpc_resp(req_json, err):
    return {
        'jsonrpc': '2.0',
        'id': _get_req_id(req_json),
        'error': {
            'code': -32600,
            'message': 'Invalid JSON RPC 2.0 request',
            'data': {
                'validation_error': err.message,
                'value': err.instance,
                'path': list(err.absolute_path)
            }
        }
    }


def _invalid_params_resp(req_json, err):
    """
    JSON Schema validation error on the params.
    """
    return {
        'jsonrpc': '2.0',
        'id': _get_req_id(req_json),
        'error': {
            'code': -32602,
            'message': err.message,
            'data': {
                'failed_validator': err.validator,
                'value': err.instance,
                'path': list(err.absolute_path)
            }
        }
    }


def _server_err_resp(req_json, err):
    """
    Server error, possibly unexpected
    """
    if hasattr(err, 'error_code'):
        code = err.error_code
    else:
        code = -32000
    resp = {
        'jsonrpc': '2.0',
        'id': _get_req_id(req_json),
        'error': {
            'code': code,
            'message': str(err)
        }
    }
    if hasattr(err, 'resp_data'):
        resp['error']['data'] = err.resp_data
    return resp


def _get_req_id(req_json):
    try:
        return req_json['id']
    except Exception:
        return None


def _missing_params_resp(req_json):
    resp = {
        'jsonrpc': '2.0',
        'id': _get_req_id(req_json),
        'error': {
            'code': -32602,
            'error': 'Missing params'
        }
    }
    return resp


def _missing_header_resp(req_json, key):
    resp = {
        'jsonrpc': '2.0',
        'id': _get_req_id(req_json),
        'error': {
            'code': -32602,
            'error': f"Header with key '{key}' required but not provided."
        }
    }
    return resp


def _invalid_header_resp(req_json, key, pattern):
    resp = {
        'jsonrpc': '2.0',
        'id': _get_req_id(req_json),
        'error': {
            'code': -32602,
            'error': f"Header with key '{key}' does not match the format '{pattern}'."
        }
    }
    return resp
