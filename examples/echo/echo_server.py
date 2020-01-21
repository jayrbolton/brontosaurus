from brontosaurus import API

api = API()

message = api.ref('message', {
    'type': 'object',
    'required': ['message'],
    'properties': {
        'message': {
            'type': 'string'
        }
    }
})


@api.method('echo', 'Is there an echo in here?')
@api.params(message)
@api.result(message)
def echo(params, headers):
    print('headers', headers)
    print('params', params)
    return {'message': params['message'] * 10}


if __name__ == '__main__':
    api.run()
