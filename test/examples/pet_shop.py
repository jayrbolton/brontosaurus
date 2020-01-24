from brontosaurus import API

desc = """
This is a sample Petstore server. You can find out more about Brontosaurus
at http://spacejam.com. For this sample, you can use the api key
special-key to test the authorization filters.
"""

api = API("Brontosaurus Petstore", desc)


pet = api.register({
    '$id': '#pet',
    'type': 'object',
    'additionalProperties': False,
    'required': ['id', 'category', 'name', 'status'],
    'properties': {
        'id': {
            'type': 'integer'
        },
        'name': {
            'type': 'string'
        },
        'photoUrls': {
            'type': 'array',
            'items': {
                'type': 'string',
                'format': 'uri'
            },
        },
        'tags': {
            'type': 'array',
            'items': {
                '$ref': '#tag'
            }
        },
        'status': {
            'type': 'string',
            'enum': ['available', 'pending', 'sold']
        }
    }
})

order = api.register({
    '$id': '#order',
    'type': 'object',
    'additionalProperties': False,
    'required': ['id', 'petId', 'quantity', 'shipDate', 'status', 'complete'],
    'properties': {
        'id': {
            'type': 'integer'
        },
        'petId': {
            'type': 'integer'
        },
        'quantity': {
            'type': 'integer',
            'minimum': 1
        },
        'shipDate': {
            'type': 'string',
            'format': 'date-time'
        },
        'status': {
            'type': 'string',
            'enum': ['placed', 'approved', 'delivered']
        },
        'complete': {
            'type': 'boolean'
        }
    }
})

user = api.register({
    '$id': '#user',
    'type': 'object',
    'additionalProperties': False,
    'required': ['id', 'username', 'email', 'password', 'userStatus'],
    'properties': {
        'id': {
            'type': 'integer'
        },
        'username': {
            'type': 'string'
        },
        'firstName': {
            'type': 'string'
        },
        'lastName': {
            'type': 'string'
        },
        'email': {
            'type': 'string',
            'format': 'email'
        },
        'password': {
            'type': 'string',
            'minLength': 7
        },
        'phone': {
            'type': 'string'
        },
        'userStatus': {
            'type': 'integer'
        }
    }
})

category = api.register({
    '$id': '#category',
    'type': 'object',
    'additionalProperties': False,
    'required': ['id', 'name'],
    'properties': {
        'id': {
            'type': 'integer'
        },
        'name': {
            'type': 'string'
        }
    }
})

tag = api.register({
    '$id': '#tag',
    'type': 'object',
    'additionalProperties': False,
    'required': ['id', 'name'],
    'properties': {
        'id': {
            'type': 'integer'
        },
        'name': {
            'type': 'string'
        }
    }
})

pet_id = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['id'],
    'properties': {
        'id': {
            'type': 'integer'
        }
    }
}


@api.method('get_pet', 'Fetch a pet by ID')
@api.params(pet_id)
@api.result(pet)
def get_pet(params, header):
    pass


pet_update = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['id'],
    'properties': {
        'id': {
            'type': 'integer'
        },
        'name': {
            'type': 'string'
        },
        'status': {
            'type': 'string'
        }
    }
}


@api.method('update_pet', 'Update a pet by ID')
@api.params(pet_update)
@api.result(pet)
def update_pet(params, headers):
    pass


# Creation of a new pet entry
new_pet = {
    'type': 'object',
    'required': ['name', 'category', 'status'],
    'additionalProperties': False,
    'properties': {
        'name': {
            'type': 'string'
        },
        'category': {
            '$ref': '#category'
        },
        'photoUrls': {
            'type': 'array',
            'items': {
                'type': 'string',
                'format': 'uri'
            }
        },
        'tags': {
            '$ref': '#tag'
        },
        'status': {
            'type': 'string',
            'enum': ['available', 'pending', 'sold']
        }
    }
}


@api.method('create_pet', 'Create a new pet entry')
@api.params(new_pet)
@api.result(pet)
def create_pet(params, headers):
    pass
