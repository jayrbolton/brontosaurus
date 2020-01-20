import sanic
import jsonschema
import jsonschema.exceptions


class Method:

    def __init__(self, name, summary, handler):
        self.name = name
        self.summary = summary
        self.handler = handler


class API:

    def __init__(self):
        """
        Create a new JSON RPC + JSON Schema API.
        """
        # Map function IDs to name, summary, func, params, result
        self.methods = {}  # type: dict
        # Map method name to function IDs
        self.method_names = {}  # type: dict
        return

    def method(self, name, summary):
        """
        Register a new RPC method.
        """
        if name in self.methods:
            raise RuntimeError(f"Method already registered: {name}")

        def wrapper(func):
            _id = id(func)
            if _id not in self.methods:
                self.methods[_id] = {}
            self.methods[_id]['name'] = name
            self.methods[_id]['summary'] = summary
            self.methods[_id]['func'] = func
            self.method_names[name] = _id
            return func
        return wrapper

    def params(self, schema):
        """
        Define a JSON schema for the RPC parameters for a method.
        """

        def wrapper(func):
            _id = id(func)
            if _id not in self.methods:
                self.methods[_id] = {}
            self.methods[_id]['params_schema'] = schema
        return wrapper

    def result(self, schema):
        """
        Define a JSON schema for the RPC result for a method.
        """

        def wrapper(func):
            _id = id(func)
            if _id not in self.methods:
                self.methods[_id] = {}
            self.methods[_id]['result_schema'] = schema
        return wrapper

    def run(self, host='0.0.0.0', port=8080, development=True, cors=False):
        """
        Run the server.
        """
        app = sanic.Sanic()

        @app.route("/", methods=['POST', 'OPTIONS'])
        def root_route(req):
            try:
                req_json = req.json
            except Exception as err:  # TODO Get more specific err class
                return sanic.response.json(_invalid_json_resp(req, err))
            try:
                jsonschema.validate(json_rpc2_schema, req_json)
            except jsonschema.exceptions.ValidationError as err:
                return sanic.response.json(_invalid_json_rpc_resp(req_json, err))
            meth_name = req_json['method']
            if meth_name not in self.method_names:
                return sanic.response.json(_unknown_method_resp(req_json, meth_name))
            meth_id = self.method_names[meth_name]
            meth = self.methods[meth_id]
            # Validate the parameters
            if 'params_schema' in meth:
                try:
                    jsonschema.validate(req_json.get('params'), meth['params_schema'])
                except jsonschema.exceptions.ValidationError as err:
                   return sanic.response.json(_invalid_params_resp(req_json, err))
            # Compute the result
            func = meth['func']
            try:
                result = func(req_json.get('params'), dict(req.headers))
            except Exception as err:
                return sanic.response.json(_server_err_resp(req_json, err))
            # Validate the result
            if development and 'result_schema' in meth:
                jsonschema.validate(result, meth['result_schema'])
            return sanic.response.json({
                'jsonrpc': '2.0',
                'id': req_json.get('id'),
                'result': result
            })
        app.run(host=host, port=port)


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
            'type': ['integer', 'string', 'null']
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
        'id': req_json.get('id'),
        'error': {
            'code': 123,  # TODO,
            'message': f'Unknown method: {meth_name}'
        }
    }


def _invalid_json_resp(req, err):
    return {
        'jsonrpc': '2.0',
        'id': None,
        'error': {
            'code': 123,  # TODO
            'message': 'Unable to parse JSON'  # TODO error message
        }
    }


def _invalid_json_rpc_resp(req_json, err):
    return {
        'jsonrpc': '2.0',
        'id': req_json.get('id'),
        'error': {
            'code': 123,  # TODO
            'message': 'Invalid JSON RPC 2.0 format',  # TODO details of schema validation failure
        }
    }


def _invalid_params_resp(req_json, err):
    """
    JSON Schema validation error on the params.
    """
    return {
        'jsonrpc': '2.0',
        'id': req_json.get('id'),
        'error': {
            'code': 123,  # TODO
            'message': err.message  # TODO
        }
    }


def _server_err_resp(req_json, err):
    """
    Server error, possibly unexpected
    """
    if hasattr(err, 'error_code'):
        code = err.error_code
    else:
        code = 123  # TODO server error code
    resp = {
        'jsonrpc': '2.0',
        'id': req_json.get('id'),
        'error': {
            'code': code,
            'message': str(err)
        }
    }
    if hasattr(err, 'resp_data'):
        resp['error']['data'] = err.resp_data
    return resp
