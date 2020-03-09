from brontosaurus.generate_docs import generate_docs

from test.examples.pet_shop import api
# from test.examples.json_schema_types import api


def test_docs():
    generate_docs(api, 'test/examples/pet_shop_api.md')
