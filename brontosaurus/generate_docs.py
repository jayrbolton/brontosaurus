"""
Generate API documentation from an API object.
"""


def generate_docs(api):
    """
    Generate documentation from an API object.
    """
    path = 'API.md'
    with open(path, 'w') as fd:
        fd.write('')
    with open(path, 'a') as fd:
        # Write titel
        fd.write(f'# {api.title}\n\n')
        # Write description
        fd.write(f'{api.desc}\n\n')
        # Write methods
        fd.write(f'## Methods\n\n')
        for (meth_name, meth_id) in api.method_names.items():
            meth = api.methods[meth_id]
            fd.write(f'### `{meth_name}`\n\n')
            fd.write(f"{meth['summary']}\n\n")
            params_schema = meth.get('params_schema')
            if params_schema:
                if '$id' in params_schema:
                    if 'title' in params_schema:
                        name = params_schema['title']
                    else:
                        name = params_schema['$id'].replace('#', '')
                    fd.write(f"**Params type:** [{name}]({params_schema['$id']})\n\n")
                else:
                    fd.write(f'#### Params\n\n')
                    fd.write(_format_type(params_schema))
            result_schema = meth.get('result_schema')
            if result_schema:
                if '$id' in result_schema:
                    if 'title' in result_schema:
                        name = result_schema['title']
                    else:
                        name = result_schema['$id'].replace('#', '')
                    fd.write(f"**Result type:** [{name}]({result_schema['$id']})\n\n")
                else:
                    fd.write(f'#### Result\n\n')
                    fd.write(_format_type(result_schema))
            print('method', meth)
        # Write types
        fd.write(f'## Data Types\n\n')
        for (_id, schema) in api.refs.items():
            if 'title' in schema:
                name = schema['title']
            else:
                name = _id.replace('#', '')  # TODO regex
            fd.write(f"### <a name={schema['$id']}>{name}</a>\n\n")
            if 'description' in schema:
                fd.write(f"{schema['description']}\n\n")
            fd.write(_format_type(schema))
    return path


def _format_type(schema):
    type_name = schema.get('type')
    if not type_name:
        return ''
    if type_name == 'object':
        return _format_obj_type(schema)


def _format_obj_type(schema):
    string = "Object with keys:\n\n"
    required = set(schema.get('required'))
    props = schema.get('properties')
    if props:
        # string += "| Property | Type | Required | Notes |\n"
        # string += "--------------------------------------\n"
        for (prop_name, prop_type) in props.items():
            type_name = prop_type.get('type')
            desc = prop_type.get('description')
            is_required = prop_name in required
            req_text = "required" if is_required else "optional"
            desc = prop_type.get('description')
            desc = '- ' + desc if desc else ''
            string += f"* `{prop_name}` - {req_text} {type_name} {desc}\n"
    string += "\n"
    return string
