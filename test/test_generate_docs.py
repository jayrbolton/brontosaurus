from brontosaurus.generate_docs import generate_docs

from test.examples.json_schema_types import api


def test_docs():
    generate_docs(api)
