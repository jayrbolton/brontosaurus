"""
Generate API documentation from an API object.
"""

# TODO table of contents


def generate_docs(api):
    """
    Generate documentation from an API object.
    """
    path = 'API.md'
    with open(path, 'w') as fd:
        fd.write('')
    with open(path, 'a') as fd:
        # Write title
        fd.write(f'# {api.title}\n\n')
        # Write description
        fd.write(f'{api.desc}\n\n')
        # Write methods
        fd.write(f'## Methods\n\n')
        for (meth_name, meth_id) in api.method_names.items():
            meth = api.methods[meth_id]
            params_schema = meth.get('params_schema')
            result_schema = meth.get('result_schema')
            fd.write(f'### {meth_name}({_format_type_short(params_schema)}) ⇒ {_format_type_short(result_schema)}\n\n')
            fd.write(f"{meth['summary']}\n\n")
            if params_schema:
                if '$id' in params_schema:
                    fd.write(f"**Parameters type:** [{params_schema['$id']}]({params_schema['$id']})\n\n")
                else:
                    fd.write(f'#### Parameters\n\n')
                    fd.write(_format_type(params_schema))
            if result_schema:
                if '$id' in result_schema:
                    fd.write(f"**Result type:** [{result_schema['$id']}]({result_schema['$id']})\n\n")
                else:
                    fd.write(f'#### Result\n\n')
                    fd.write(_format_type(result_schema))
            print('method', meth)
        # Write types
        fd.write(f'# Data Types\n\n')
        for (_id, schema) in api.refs.items():
            fd.write(f"## <a name={schema['$id']}>[{schema['$id']}]({schema['$id']})</a>\n\n")
            if 'description' in schema:
                fd.write(f"{schema['description']}\n\n")
            fd.write(_format_type(schema))
    print(f'Wrote docs to {path}')
    return path


def _format_type(schema):
    type_name = schema.get('type')
    if not type_name:
        return ''
    if type_name == 'object':
        return _format_obj_type(schema)


def _format_obj_type(schema, indent=0):
    string = "JSON object with properties:\n\n"
    required = set(schema.get('required'))
    props = schema.get('properties')
    if props:
        # string += "| Property | Type | Required | Notes |\n"
        # string += "--------------------------------------\n"
        for (prop_name, prop_type) in props.items():
            is_required = prop_name in required
            string += _format_obj_field(prop_name, prop_type, is_required, indent=0)
    string += "\n"
    return string


def _format_obj_field(prop_name, prop_type, is_required, indent=0):
    string = ("  " * indent) + "* "
    desc = prop_type.get('description')
    req_text = "required" if is_required else "optional"
    desc = prop_type.get('description')
    desc = '- ' + desc if desc else ''
    string += f'`"{prop_name}"` – {req_text} {_format_type_short(prop_type)}\n'
    return string


def _format_type_short(typ):
    ref = typ.get('$ref')
    if ref:
        return f"[{ref}]({ref})"
    _id = typ.get('$id')
    if _id:
        return f"[{_id}]({_id})"
    type_name = typ.get('type')
    if not type_name:
        return ''
    if type_name == 'array':
        return "array of " + _format_type_short(typ['items'])
    string = f"{type_name}"
    if type_name == 'string':
        if typ.get('format'):
            string += f" (format: {typ.get('format')})"
        if typ.get('enum'):
            options = ', '.join(f'"{x}"' for x in typ['enum'])
            string += f" (must be one of {options})"
    if type_name == 'integer':
        if typ.get('minimum'):
            string += f" (minimum: {typ['minimum']})"
    return string
