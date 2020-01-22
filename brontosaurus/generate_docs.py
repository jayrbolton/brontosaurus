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
                fd.write(f'#### Params\n\n')
                fd.write(_format_type(params_schema))
            result_schema = meth.get('result_schema')
            if result_schema:
                fd.write(f'#### Result\n\n')
                fd.write(_format_type(result_schema))
            print('method', meth)
        # Write types
        fd.write(f'## Data Types\n\n')
        for (type_name, ref) in api.refs.items():
            fd.write(f'### {type_name}\n\n')
            desc = ref['desc']
            fd.write(f'{desc}\n\n')
            fd.write(_format_type(ref['schema']))
    return path


def _format_type(schema):
    type_name = schema.get('type')
    if not type_name:
        return ''
    if type_name == 'object':
        return _format_obj_type(schema)


def _format_obj_type(schema):
    string = "Object with keys:\n\n"
    title = schema.get('title')
    desc = schema.get('description')
    if title and desc:
        string += f"{title} - {desc}\n\n"
    elif title or desc:
        string += f"{title or desc}\n\n"
    required = set(schema.get('required'))
    props = schema.get('properties')
    if props:
        # string += "| Property | Type | Required | Notes |\n"
        # string += "--------------------------------------\n"
        for (prop_name, prop_type) in props.items():
            type_name = prop_type.get('type')
            title, desc = prop_type.get('title'), prop_type.get('description')
            is_required = prop_name in required
            req_text = "required" if is_required else "optional"
            desc = prop_type.get('description')
            desc = '- ' + desc if desc else ''
            string += f"* `{prop_name}` - {req_text} {type_name} {desc}\n"
    string += "\n"
    return string
