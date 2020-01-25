from brontosaurus.generate_docs import generate_docs

from test.examples.pet_shop import api


def test_docs():
    generate_docs(api)
