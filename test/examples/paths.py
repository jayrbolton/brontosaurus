from brontosaurus import API

desc = """
Test server showing multiple sub-paths, each with a different RPC API.
"""

api = API("Paths Example", desc, doc_path='test/examples/docs/paths-root-api.md')
subpath1 = api.subpath(
    path='subpath1',
    title='Subpath One',
    desc='First Subpath example',
    doc_path='test/examples/docs/paths-subpath1.md'
)
subpath2 = api.subpath(
    path='subpath2',
    title='Subpath Two',
    desc='Second Subpath example',
    doc_path='test/examples/docs/paths-subpath2.md'
)


@api.method('hello', 'Hello method from root')
def root_hello(params, header):
    return 'hello from root'


@subpath1.method('hello', 'Hello method from subpath1')
def subpath1_hello(params, header):
    return 'hello from subpath1'


@subpath2.method('hello', 'Hello method from subpath2')
def subpath2_hello(params, header):
    return 'hello from subpath2'
