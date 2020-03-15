from brontosaurus import API

desc = """
This is a sample Petstore server. You can find out more about Brontosaurus
at http://spacejam.com. For this sample, you can use the api key
special-key to test the authorization filters.
"""

api = API("Brontosaurus Petstore", desc, doc_path='test/examples/docs/pet_shop_api.md')


# Pet status type
status = {
    'type': 'string',
    'enum': ['available', 'pending', 'sold']
}


# Saved pet schema
pet = api.register({
    '$id': '#pet',
    'type': 'object',
    'additionalProperties': False,
    'required': ['id', 'category', 'name', 'status'],
    'properties': {
        'id': {
            'type': 'integer',
            'examples': [0, 1, 2]
        },
        'category': {
            '$ref': '#category'
        },
        'name': {
            'type': 'string',
            'examples': ['Buster', 'Lil Doof']
        },
        'photoUrls': {
            'type': 'array',
            'items': {
                'type': 'string',
                'format': 'uri'
            },
            'examples': [['https://spacejam.com/img/p-jamlogo.gif']]
        },
        'tags': {
            'type': 'array',
            'items': {
                '$ref': '#tag'
            }
        },
        'status': status
    }
})

# Saved order schema
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
        'status': status,
        'complete': {
            'type': 'boolean'
        }
    }
})

# Params for updating or creating an order
new_order = {
    'type': 'object',
    'required': ['petId', 'quantity'],
    'properties': {
        'petId': {
            'type': 'integer',
            'minimum': 0
        },
        'quantity': {
            'type': 'integer',
            'minimum': 1
        }
    }
}

# Schema for an existing user
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

# Schema for an existing category with an ID
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

# Schema for an existing tag with an ID
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

# Generic schema for fetching a pet, order, or user using an ID
id_schema = {
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
@api.params(id_schema)
@api.result(pet)
def get_pet(params, header):
    pass


# Fields you can update for a pet
pet_update = {
    'type': 'object',
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
            'type': 'array',
            'items': {
                '$ref': '#tag'
            }
        },
        'status': status
    }
}

# Fields for creating a new pet
pet_new = {
    **pet_update,
    'required': ['name', 'category', 'status'],
}  # type: dict

# Fields for updating a pet by ID
update_pet_params = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['id', 'pet'],
    'properties': {
        'id': {
            'description': 'ID of the pet you want to update.',
            'type': 'integer'
        },
        'pet': pet_update
    }
}


@api.method('update_pet', 'Update a pet by ID')
@api.params(update_pet_params)
@api.result(pet)
def update_pet(params, headers):
    pass


@api.method('create_pet', 'Create a new pet entry')
@api.params(pet_new)
@api.result(pet)
def create_pet(params, headers):
    pass


@api.method('delete_pet', 'Delete a pet entry by ID')
@api.params(id_schema)
@api.require_header('Authorization', r'^token .+$')
def delete_pet(params, headers):
    pass


statuses = {
    'type': 'object',
    'additionalProperties': False,
    'required': 'any_status',
    'properties': {
        'any_status': {
            'type': 'array',
            'minLength': 1,
            'items': status
        }
    }
}


pet_list = {
    'type': 'array',
    'items': {'$ref': '#pet'}
}


@api.method('find_pet_by_status', 'Find a pet that has any of the given statuses.')
@api.params(statuses)
@api.result(pet_list)
def find_pet_by_status(params, headers):
    pass


tag_query = {
    'type': 'object',
    'additionalProperties': False,
    'required': 'any_tag',
    'properties': {
        'any_tag': {
            'type': 'array',
            'minLength': 1,
            'items': {
                'type': 'string',
                'title': 'Tag Name'
            }
        }
    }
}


@api.deprecated('This method is no longer supported for some reason or another.')
@api.method('find_pet_by_tags', 'Find a pet that has any of the given tags.')
@api.params(tag_query)
@api.result(pet_list)
def find_by_tags(parasms, headers):
    pass


store_inventory_statuses = {
    'type': 'object',
    'required': ['available', 'pending', 'sold'],
    'properties': {
        'available': {
            'type': 'integer',
            'minimum': 0
        },
        'pending': {
            'type': 'integer',
            'minimum': 0
        },
        'sold': {
            'type': 'integer',
            'minimum': 0
        }
    }
}


@api.method('get_store_inventory', 'Return a map of statuses to quantities')
@api.result(store_inventory_statuses)
def pet_store_inventory(params, headers):
    pass


@api.method('get_order', 'Get a purchase order by ID')
@api.params(id_schema)
@api.result(order)
def get_order(params, headers):
    pass


@api.method('delete_order', 'Delete a purchase order by ID')
@api.params(id_schema)
def delete_order(params, headers):
    pass


@api.method('create_order', 'Place an order for a pet.')
@api.params(new_order)
@api.result(order)
def create_order(params, headers):
    pass


username_query = {
    'type': 'object',
    'required': ['username'],
    'additionalProperties': False,
    'properties': {
        'username': {
            'type': 'string',
            'minLength': 3
        }
    }
}


@api.method('get_user', 'Fetch a user by username')
@api.params(username_query)
@api.result(user)
def get_user(params, headers):
    pass


new_user = {
    'description': 'Properties to set for the user',
    'type': 'object',
    'properties': {
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
        }
    }
}

user_update_params = {
    'type': 'object',
    'required': ['username_to_update', 'user'],
    'properties': {
        'username_to_update': {
            'type': 'string',
            'description': "Username for the account we'd like to update"
        },
        'user': new_user
    }
}


@api.method('update_user', 'Update a user')
@api.params(user_update_params)
@api.result(user)
def update_user(params, headers):
    pass


@api.method('delete_user', 'Delete a user')
@api.params(id_schema)
def delete_user(params, headers):
    pass


login_params = {
    'type': 'object',
    'required': ['username', 'password'],
    'additionalProperties': False,
    'properties': {
        'username': {
            'type': 'string',
            'minLength': 3
        },
        'password': {
            'type': 'password',
            'minLength': 7
        }
    }
}


@api.method('login', 'Logs user into the system')
@api.params(login_params)
def login(params, headers):
    pass


@api.method('logout', 'Logs out a currently logged-in user')
def logout(params, headers):
    pass


@api.method('create_user', 'Create a new user account')
@api.params(new_user)
@api.result(user)
def create_user(params, headers):
    pass
