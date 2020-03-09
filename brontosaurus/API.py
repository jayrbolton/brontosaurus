import multiprocessing
import brontosaurus.exceptions
from brontosaurus.create_sanic_server import create_sanic_server
from brontosaurus.generate_docs import generate_docs
from brontosaurus.utils.find_keys import find_keys


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
        # Map schema reference ids to a list of method IDs that use them
        self.methods_using = {}  # type: dict
        self.subpaths = {}  # type: dict
        return

    def method(self, name, summary):
        """
        Register a new RPC method.
        """
        if name in self.methods:
            raise brontosaurus.exceptions.MethodAlreadyExists(f"Method already registered: {name}")

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

    def _get_ref(self, schema, method_id=None):
        _id = schema.get('$id')
        if not _id:
            return
        if _id[0] != '#':
            raise RuntimeError("Type IDs must be in the form of: `#id`")
        if _id in self.refs and schema != self.refs[_id]:
            msg = f"Schema with $id '{_id}' has different definitions"
            raise brontosaurus.exceptions.SchemaReferenceMismatch(msg)
        elif _id not in self.refs:
            self.refs[_id] = schema

    def _save_method_using(self, schema, method_id=None):
        for _id in find_keys(schema, ['$ref', '$id']):
            if _id not in self.methods_using:
                self.methods_using[_id] = set()
            self.methods_using[_id].add(method_id)

    def register(self, schema):
        """
        Register a reference type with an $id
        """
        if '$id' not in schema:
            raise TypeError('Schema must have an "$id" field')
        self._get_ref(schema)
        return schema

    def params(self, schema):
        """
        Define a JSON schema for the RPC parameters for a method.
        """
        self._get_ref(schema)

        def wrapper(func):
            _id = id(func)
            if _id not in self.methods:
                self.methods[_id] = {}
            self.methods[_id]['params_schema'] = schema
            self._save_method_using(schema, _id)
            return func
        return wrapper

    def result(self, schema):
        """
        Define a JSON schema for the RPC result for a method.
        """
        self._get_ref(schema)

        def wrapper(func):
            _id = id(func)
            if _id not in self.methods:
                self.methods[_id] = {}
            self.methods[_id]['result_schema'] = schema
            self._save_method_using(schema, _id)
            return func
        return wrapper

    def require_header(self, key, pattern=None):
        """
        Require an HTTP(S) header with an optionally enforced string or regex
        pattern for the value.
        """
        def wrapper(func):
            _id = id(func)
            if _id not in self.methods:
                self.methods[_id] = {}
            if 'headers' not in self.methods[_id]:
                self.methods[_id]['headers'] = []
            self.methods[_id]['headers'].append((key, pattern))
            return func
        return wrapper

    def deprecated(self, reason):
        """
        Mark a method as deprecated with a reason.
        """
        def wrapper(func):
            _id = id(func)
            if _id not in self.methods:
                self.methods[_id] = {}
            self.methods[_id]['deprecated'] = reason
            return func
        return wrapper

    def subpath(self, path, title, desc):
        """
        Create a nested API under a subpath.
        """
        if path in self.subpaths:
            raise RuntimeError(f"Subpath already taken: `{path}`")
        self.subpaths[path] = API(title, desc)
        return self.subpaths[path]

    def run(self, host='0.0.0.0', port=8080, development=True, cors=False, workers=2, doc_path='API.md'):
        """
        Run the server.
        """
        if not workers:
            workers = multiprocessing.cpu_count()
        app = create_sanic_server(self, workers, cors, development)
        if development:
            generate_docs(self, doc_path)
        app.run(host=host, port=port, workers=workers)
