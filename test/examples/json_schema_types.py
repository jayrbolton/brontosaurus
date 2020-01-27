from brontosaurus import API

desc = """
This is a non-server that is for testing documentation generation of all the
variations of draf-07 JSON Schema type annotations.
"""

# TODO array with additional item crap nested inside an object

api = API("JSON Schema Types Test", desc)

api.register({
    '$id': '#array-empty-items',
    'items': {}
})


api.register({
    "$id": "#array-additional-items",
    "description": "additionalItems as schema",
    "items": [{}],
    "additionalItems": {"type": "integer"}
})


api.register({
    '$id': '#array-no-additional-items',
    "description": "items is schema, no additionalItems",
    "items": {},
    "additionalItems": False
})

api.register({
    '$id': '#array-items-no-additional',
    "description": "array of items with no additionalItems",
    "items": [{}, {}, {}],
    "additionalItems": False
})

api.register({
    '$id': '#obj-array-items-no-additional',
    "description": "array of items with no additionalItems inside obj",
    "type": "object",
    "properties": {
        "arr": {
            "type": "array",
            "items": [{}, {}, {}],
            "additionalItems": False
        }
    }
})

api.register({
    '$id': '#array-items-no-items-no-additional',
    "description": "additionalItems as false without items",
    "additionalItems": False
})

api.register({
    '$id': '#array-items',
    "description": "additionalItems are allowed by default",
    "items": [{"type": "integer"}],
})

# TODO
api.register({
    '$id': '#obj-no-addl-props',
    "description": "additionalProperties being false does not allow other properties",
    "properties": {"foo": {}, "bar": {}},
    "patternProperties": {"^v": {}},
    "additionalProperties": False
})

# TODO
api.register({
    '$id': '#obj-non-ascii-pattern',
    "description": "non-ASCII pattern with additionalProperties",
    "patternProperties": {"^á": {}},
    "additionalProperties": False
})

# TODO
api.register({
    '$id': '#obj-additional-props-schema',
    "description": "additionalProperties allows a schema which should validate",
    "properties": {"foo": {}, "bar": {}},
    "additionalProperties": {"type": "boolean"}
})

# TODO
api.register({
    '$id': '#obj-only-additional-props',
    "description": "additionalProperties can exist by itself",
    "additionalProperties": {"type": "boolean"}
})

# TODO
api.register({
    '$id': '#obj-basic',
    "description": "additionalProperties are allowed by default",
    "properties": {"foo": {}, "bar": {}},
})

# TODO
api.register({
    '$id': '#obj-allOf',
    "description": "additionalProperties should not look in applicators",
    "allOf": [{"properties": {"foo": {}}}],
    "additionalProperties": {"type": "boolean"}
})
