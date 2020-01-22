import multiprocessing
import brontosaurus.exceptions
from brontosaurus.create_sanic_server import create_sanic_server
from brontosaurus.generate_docs import generate_docs


class API:
    """
    Class for a brontosaurus API object.
    """

    def __init__(self, title, desc):
        """
        Create a new JSON RPC + JSON Schema API.
        """
        self.title = title
        self.desc = desc
        # Map function IDs to name, summary, func, params, result
        self.methods = {}  # type: dict
        # Map method name to function IDs
        self.method_names = {}  # type: dict
        # Map names to JSON schemas for generating documentation
        self.refs = {}  # type: dict
        return

    def method(self, name, summary):
        """
        Register a new RPC method.
        """
        if name in self.methods:
            raise brontosaurus.exceptions.MethodAlreadyExists(f"Method already registered: {name}")

        def wrapper(func):
            print('func?!', func)
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
            return func
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
            return func
        return wrapper

    def ref(self, name, desc, schema):
        if name in self.refs:
            raise brontosaurus.exceptions.SchemaAlreadyExists(f"Schema already exists: {name}")
        self.refs[name] = {'schema': schema, 'desc': desc}
        return schema

    def run(self, host='0.0.0.0', port=8080, development=True, cors=False, workers=None):
        """
        Run the server.
        """
        if not workers:
            workers = multiprocessing.cpu_count()
        app = create_sanic_server(self, workers, cors, development)
        generate_docs(self)
        app.run(host=host, port=port, workers=workers)
