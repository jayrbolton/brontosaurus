from brontosaurus import API
import time

api = API()  # Server options go in here

# Schema for the ID of a training model
model_id = {
    'title': 'Model ID',
    'description': 'Unique integer ID representing a training model',
    'type': 'integer',
    'minimum': 1
}

# JSON schema for an existing machine learning model
# Wrapping the schema in "ref" displays it in the docs
model = api.ref({
    'description': 'Existing machine learning model',
    'type': 'object',
    'required': ['id', 'name', 'type', 'data_source_id'],
    'properties': {
        'id': model_id,
        'name': {
            'type': 'string',
            'description': 'User-assigned name'
        },
        'type': {
            'type': 'string',
            'enum': ['regression', 'binary', 'multiclass']
        },
        'data_source_id': {
            'type': 'integer',
            'description': 'Unique identifier of the data source used for training'
        }
    }
})

# JSON schema for creating a new training model. Does not have ID
new_model = api.ref({
    'title': 'New machine learning model',
    'type': 'object',
    'required': ['name', 'type', 'data_source_id'],
    'properties': {
        'name': model['properties']['name'],
        'type': model['properties']['type'],
        'data_source_id': model['properties']['data_source_id']
    }
})

# Schema for the results of using a model to predict output from input
prediction = api.ref({
    'type': 'object',
    'title': 'Machine learning prediction',
    'description': 'Either the "label" (binary/multiclass) or "val" (regression) prop will be present',
    'anyOf': [
        {'required': ['label']},
        {'required': ['val']}
    ],
    'properties': {
        'labels': {
            'type': 'object',
            'description': 'Each key is a predicted label for binary/multiclass models',
            'properties': {
                '.*': {
                    'type': 'number',
                    'title': 'Predicton score, 0-1',
                    'minimum': 0,
                    'maximum': 1
                }
            }
        },
        'val': {
            'title': 'Predicted value',
            'description': 'Numeric predicted output for regression models',
            'type': 'number'
        }
    }
})


@api.method('train_model', 'Create a new training model')
@api.params(new_model)
@api.result(model_id)
def train_model(params, headers):
    # Train a model against some dataset...
    # You can access params['name'], params['type'], and params['data_source_id']
    print('Doing some fake training to create the model...')
    time.sleep(1)
    return 123


@api.method('upload_dataset', 'Upload a csv of data to use for training')
@api.multipart_upload(['text/csv'])
@api.require_header('Authorization', r'^token .+$')
def upload_dataset(params, headers, csv):
    # Do some authentication using a header
    # Upload the csv to a file store
    # Create a database record for the dataset, generating an ID
    with open('filestore/uuid.csv', 'a') as fd:
        for chunk in csv.iter_chunks:
            fd.write(chunk)
    time.sleep(1)
    return 123


@api.method('predict', 'Generate a prediction for some data using a model')
@api.params(model_id)
@api.result(prediction)
def predict(model_id, headers):
    # model = fetch_by_id(model_id)
    print('Using an existing model to create an output prediction from some input...')
    time.sleep(1)
    return prediction


if __name__ == '__main__':
    # Run the server
    api.run()  # Server options
