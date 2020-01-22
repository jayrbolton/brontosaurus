"""
Generate the sanic server object from a brontosaurus API object.
"""
import sanic
import jsonschema.exceptions
import traceback


def create_sanic_server(api, workers, cors, development):
    app = sanic.Sanic()

    @app.route("/", methods=['OPTIONS', 'PUT', 'POST', 'GET', 'DELETE'])
    def root_route(req):
        try:
            req_json = req.json
        except sanic.exceptions.InvalidUsage as err:
            return sanic.response.json(_invalid_json_resp(req, err), 400)
        try:
            jsonschema.validate(req_json, json_rpc2_schema)
        except jsonschema.exceptions.ValidationError as err:
            return sanic.response.json(_invalid_json_rpc_resp(req_json, err), 400)
        meth_name = req_json['method']
        if meth_name not in api.method_names:
            return sanic.response.json(_unknown_method_resp(req_json, meth_name), 400)
        meth_id = api.method_names[meth_name]
        meth = api.methods[meth_id]
        # Validate the parameters
        if 'params_schema' in meth:
            if req_json.get('params') is None:
                return sanic.response.json(_missing_params_resp(req_json), 400)
            try:
                jsonschema.validate(req_json.get('params'), meth['params_schema'])
            except jsonschema.exceptions.ValidationError as err:
                return sanic.response.json(_invalid_params_resp(req_json, err), 400)
        # Compute the result
        func = meth['func']
        try:
            result = func(req_json.get('params'), dict(req.headers))
        except Exception as err:
            return sanic.response.json(_server_err_resp(req_json, err), 500)
        # Validate the result
        if development and 'result_schema' in meth:
            jsonschema.validate(result, meth['result_schema'])
        return sanic.response.json({
            'jsonrpc': '2.0',
            'id': _get_req_id(req_json),
            'result': result
        })

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
        print(err)
        traceback.print_exc()
        return sanic.response.raw(b'', 500)

    if cors:
        # Handle cors response headers
        @app.middleware('response')
        async def cors_resp(req, res):
            res.headers['Access-Control-Allow-Origin'] = '*'
            res.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
            res.headers['Access-Control-Allow-Headers'] = '*'
    return app


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
