# brontosaurus - streamlined JSON APIs

Write small and fast API servers using:
* Sanic - for a fast async http server
* JSON Schema - for request and response validation and documentation
* JSON RPC 2.0 - for a simple surrounding format
* Python - for all your easy to read glue code

Some benefits:
* Automatic request validation
* Autogenerated API documentation in markdown
* Removes various RPC setup boilerplate
* Handles bulk requests asynchronously with no extra code
* Sets default values in requests and responses automatically
* Automatically validates responses during development/test mode
* Handles binary file uploads and responses

It is opinionated but customizable. The APIs are not resource-based, but instead use a method-call style from [JSON RPC 2.0](https://www.jsonrpc.org/specification) specification (for better or worse).

**View a [quick code example](test/examples/pet_shop)** along with its **[auto-generated documentation](test/examples/pet_shop_api.md)**.

## API and Usage

### `API(title, description)`

Create a new instance of the API object, which can be used to register methods and run the server.

```py
from brontosaurus import API

api = API("Example API", "This is an example API server.")
```

### ` @api.method(name, summary)`

Register a method name and a short description. Used as a decorator around a function that handles the method.

The function receives the method parameters and the request headers as dictionaries.

```py
@api.method('no_op', 'Does nothing')
def no_op(params, headers):
    pass
```

### ` @api.params(json_schema: dict)`

Set the JSON Schema for the parameters for a method. Used as a decorator around
a method handler function. Documentation for your parameters can go inside the
`title` and `description` properties in your schema.

```py
# JSON schema for some message
message = {
    'type': 'object',
    'required': ['message'],
    'properties': {
        'message': {
            'description': 'Any message that you want',
            'type': 'string',
        }
    }
}

@api.method('log', 'Logs something in the backend')
@api.params(message)
def no_op(params, headers):
    logger.info(params)
```

See the [JSON Schema](https://json-schema.org/understanding-json-schema/) guide for detailed information on how to write these schemas.

If you run the server (see below), you can now make the following request:

```sh
$ curl -d '{"method": "log", "params": {"message": "hello world"}}'
```

### ` @api.result(json_schema: dict)`

Set the JSON Schema for the result for a method, useful for documentation and
tests. Used as a decorator around a method handler function.

```py
# JSON schema for the params and the result
echo_message = {
    'type': 'object',
    'required': ['message'],
    'properties': {
        'message': {
            'type': 'string'
        }
    }
}

@api.method('echo', 'Repeat a message back to you')
@api.params(echo_message)
@api.result(echo_message)
def echo(params, headers):
    return {'message': params['message']}
```

Now you can make the following request:

```sh
$ curl -d '{"method": "echo", "params": {"message": "hello world"}}'
> {"jsonrpc": "2.0", "id": null, "result": {"message": "hello world"}}
```

### `api.register(type_name: str, json_schema: dict)`

Register a JSON schema to be displayed in the API documentation. It does not
affect the API, and only returns a plain dict of the schema.

Registered schemas must have an `"$id"` field, which will be used as its type name in the documentation. Typically these types are prepended with the hash symbol: `"#name"`.

```py
login_schema = api.register('login', {
    '$id': '#login',
    'title': 'Login data',
    'type': 'object',
    'properties': {
        'password': {
            'type': 'string',
            'minLength': 7,
        },
        'email': {
            'type': 'string',
            'format': 'idn-email'
        }
    }
})
```

Now, when you generate the documentation by running the server, the "login" schema will appear in the documentation. Anywhere that the schema is used in a method, a link will be generated to the documentation for this type.

### `api.run(**kwargs)`

Run the server.

In development mode, the documentation file will be generated. Also, the method
results will be validated against their JSON Schemas (but not in production).

Valid keyword arguments:

* `host: str` - hostname to use (defaults to `'0.0.0.0'`)
* `port: int` - port to use for the server (defaults to `8080`)
* `development: bool` - whether we are in development mode (defaults to `True`)
* `cors: bool` - whether to fully enable cross origin requests (defaults to `False`)
* `workers: int` - how many async server workers to run (defaults to 2)
* `doc_path: str` - path (relative to the directory where the server runs) of the generated documentation. Ignored if not in development mode.

#### Development mode

Development mode has the following effects:

* Markdown documentation is generated for your API(s) whenever the server is started
* Response JSON structures are validated against their schemas
* Logging level is set to DEBUG

## Development

### Run the tests

Install `poetry` with `pip install poetry`. Install dependencies with `poetry
install`.

Run the tests

```sh
make test
```

### Contribution

Open an issue or PR
