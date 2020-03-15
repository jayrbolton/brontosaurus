"""
Generate API documentation from an API object.
"""
import json


def generate_docs(api):
    # Generate root api docs
    generate_single_docs(api)
    # Generate subpath api docs
    for (_, sub_api) in api.subpaths.items():
        generate_single_docs(sub_api)


def generate_single_docs(api):
    """
    Generate documentation from an API object.
    """
    path = api.doc_path
    with open(path, 'w') as fd:
        fd.write('')
    with open(path, 'a') as fd:
        # Write title
        fd.write(f'# {api.title}\n\n')
        # Write description
        fd.write(f'{api.desc}\n\n')
        # Table of contents
        fd.write(f'## Table of Contents\n\n')
        if api.methods:
            fd.write(f'[Methods](#methods) ({len(api.methods)} total)\n')
            for (_id, meth) in api.methods.items():
                deprec_reason = meth.get('deprecated')
                if deprec_reason:
                    fd.write(f'* ~~[{meth["name"]}](#{meth["name"]})~~\n')
                else:
                    fd.write(f'* [{meth["name"]}](#{meth["name"]})\n')
            fd.write('\n')
        if api.refs:
            fd.write(f'[Data Types](#datatypes) ({len(api.refs)} total)\n')
            for (_id, schema) in api.refs.items():
                fd.write(f'* [{_id}]({_id})\n')
            fd.write('\n')
        # Write methods
        fd.write(f'## <a name="methods">Methods</a>\n\n')
        for (meth_name, meth_id) in api.method_names.items():
            meth = api.methods[meth_id]
            meth_title = _get_method_signature(meth)
            params_schema = meth.get('params_schema')
            result_schema = meth.get('result_schema')
            deprec_reason = meth.get('deprecated')
            fd.write(f'### <a name=\'{meth["name"]}\'>' + meth_title + '</a>\n\n')
            if deprec_reason:
                fd.write(f'**This method is deprecated:** {deprec_reason}\n\n')
            fd.write(f"{meth['summary']}\n\n")
            if params_schema:
                if '$id' in params_schema:
                    fd.write(f"**Parameters type:** [{params_schema['$id']}]({params_schema['$id']})\n\n")
                else:
                    fd.write(f'**Parameters:** ')
                    fd.write(_format_generic_json(params_schema) + '\n')
            else:
                fd.write(f"**No parameters**\n\n")
            required_headers = meth.get('headers')
            if required_headers:
                fd.write(f"**Required headers**:\n\n")
                for (key, pattern) in required_headers:
                    if pattern:
                        fd.write(f' * `{key}` must have format "`{pattern}`"\n')
                    else:
                        fd.write(f" * `{key}`\n")
                fd.write("\n")
            if result_schema:
                if '$id' in result_schema:
                    fd.write(f"**Result type:** [{result_schema['$id']}]({result_schema['$id']})\n\n")
                else:
                    fd.write(f'**Result:** ')
                    fd.write(_format_generic_json(result_schema) + '\n')
            else:
                fd.write(f"**No results**\n\n")
        # Write types
        fd.write(f'# <a name="datatypes">Data Types</a>\n\n')
        for (_id, schema) in api.refs.items():
            id_without_hash = _id.replace('#', '')
            fd.write(f"## <a name=\"{id_without_hash}\">[{schema['$id']}]({schema['$id']})</a>\n\n")
            if 'description' in schema:
                fd.write(f"{schema['description']}\n\n")
            if _id in api.methods_using:
                methods_using = api.methods_using[_id]
                if methods_using:
                    method_names = [api.methods[mid]['name'] for mid in methods_using]
                    method_names_str = ', '.join(f"[{n}](#{n})" for n in method_names)
                    fd.write(f"Methods using this type: {method_names_str}\n\n")
            fd.write(_format_generic_json(schema) + '\n')
    return path


def _format_keyval(key, val, parent, obj_indent):
    """
    Return a special format for a key-val entry in a JSON object.
    """
    if key == '$id' or key == 'type' or key == '$ref':
        return False
    elif key == 'enum':
        enum_names = ', '.join(f'`{json.dumps(v)}`' for v in val)
        return f'Must be one of: {enum_names}\n'
    elif key == 'examples':
        ex = ', '.join(f'`{json.dumps(v)}`' for v in val)
        return f'Examples: {ex}\n'
    elif key == 'required':
        if not isinstance(val, list):
            val = [val]
        prop_names = ', '.join(val)
        return f'Required fields: **{prop_names}**\n'
    elif key == 'properties':
        return 'Properties:\n' + _format_obj_props(val, obj_indent + 1, parent)
    elif key == 'additionalProperties':
        if val is False:
            return 'No extra properties allowed\n'
        elif val is True:
            return 'Additional properties are allowed\n'
        elif val:
            return 'Additional properties:\n' + _format_generic_json(val, obj_indent + 1, parent) + '\n'
    elif key == 'additionalItems':
        if val is False:
            return 'No extra elements allowed\n'
        elif val is True:
            return 'Additional elements are allowed\n'
        elif val:
            return 'Additional elements:\n' + _format_generic_json(val, obj_indent + 1, parent) + '\n'
    elif (key == 'allOf' or key == 'anyOf') and val:
        if key == 'allOf':
            string = 'Must match all of:\n'
        else:
            string = 'Must match any of:\n'
        indent = obj_indent + 1
        for typ in val:
            string += ('  ' * indent) + '1. ' + _format_generic_json(val, indent + 1, parent)
        return string
    elif key == 'patternProperties':
        return 'Pattern properties:\n' + _format_obj_props(val, obj_indent + 1, parent)
    elif key == 'items' and isinstance(val, list) and val:
        string = f'Elements:\n'
        indent = obj_indent + 1
        for (idx, typ) in enumerate(val):
            string += ('  ' * indent) + f'* Item {idx}: ' + _format_generic_json(typ, indent + 1, parent)
        return string
    elif key == 'description':
        return f'Description: {val}\n'


def _format_obj_props(props, indent, parent):
    """
    Format a set of property name and type values for an object schema.
    """
    string = ''
    for (prop, typ) in props.items():
        string += ('  ' * indent) + f'* `"{prop}"` – {_format_generic_json(typ, indent + 1, prop, parent)}'
    return string


def _format_obj_prefix(schema, indent, parent, prop_name):
    """
    Create a string prefix (possibly None) for a schema object.
    Usually this will show the schema's type and whether it is required in any parent object.
    """
    if not isinstance(schema, dict):
        return None
    string = ''
    typ = schema.get('type')
    if parent:
        required = set(parent.get('required', set()))
        if prop_name and prop_name in required:
            string = 'required '
    if schema.get('$ref'):
        ref = schema['$ref']
        string += f"**[{ref}]({ref})**"
    elif _is_obj(schema):
        string += 'JSON object'
    elif _is_array(schema):
        string += 'JSON array'
    elif typ:
        string += typ
    return string


def _format_generic_json(data, obj_indent=0, prop_name=None, parent=None):
    """
    Render any JSON serializable data structure as bulleted markdown.
    Special formatting for JSON schemas are injected using:
    - _format_keyval
    - _format_obj_prefix
    """
    string = ''
    if isinstance(data, dict) and not data:
        return 'any type\n'
    elif isinstance(data, list) and not data:
        return 'empty array\n'
    prefix = _format_obj_prefix(data, obj_indent, parent, prop_name)
    if prefix:
        string += prefix + '\n'
    if isinstance(data, dict):
        for (key, val) in data.items():
            sub = _format_generic_json(val, obj_indent + 1, prop_name, parent)
            keyval = _format_keyval(key, val, data, obj_indent)
            if keyval is False:
                continue
            if keyval:
                string += ('  ' * obj_indent) + '* ' + keyval
                continue
            string += ('  ' * obj_indent) + f'* {key}: '
            if isinstance(val, dict):
                if not val:
                    string += 'any type\n'
                else:
                    string += f'{sub}'
            elif isinstance(val, list):
                if not val:
                    string += f'empty array\n'
                else:
                    string += f'array of:\n{sub}'
            else:
                string += f'{sub}\n'
        return string
    elif isinstance(data, list):
        for (idx, val) in enumerate(data):
            sub = _format_generic_json(val, obj_indent + 1, prop_name, parent)
            string += ('  ' * obj_indent) + '* '
            if isinstance(val, dict):
                if val:
                    string += f'\n{sub}'
                else:
                    string += 'any type\n'
            elif isinstance(val, list):
                if val:
                    string += f'array of:\n{sub}'
                else:
                    string += 'empty array\n'
            else:
                string += f'{sub}\n'
        return string
    else:
        return str(data)


def _get_method_signature(method):
    """
    Fetch the method name in the form of function signature.
    """
    meth_name = method['name']
    params_schema = method.get('params_schema')
    meth_title = f'{meth_name}({_format_type_short(params_schema)})'
    result_schema = method.get('result_schema')
    if result_schema:
        meth_title += f' ⇒ {_format_type_short(result_schema)}'
    deprec_reason = method.get('deprecated')
    if deprec_reason:
        meth_title = '~~' + meth_title + '~~'
    return meth_title


def _format_type_short(schema):
    """
    Return a short type name for a schema, with no linebreaks or inner details
    Examples: "object", "array", "#type_id", "integer", "string"
    """
    if schema == {}:
        return 'any type'
    if not schema:
        return ''
    ref = schema.get('$ref')
    if ref:
        return f"[{ref}]({ref})"
    _id = schema.get('$id')
    if _id:
        return f"[{_id}]({_id})"
    type_name = schema.get('type')
    if not type_name:
        return ''
    if type_name == 'array':
        return "array of " + _format_type_short(schema['items'])
    string = f"{type_name}"
    if type_name == 'string':
        if schema.get('format'):
            string += f" (format: {schema.get('format')})"
        if schema.get('enum'):
            options = ', '.join(f'"{x}"' for x in schema['enum'])
            string += f" (must be one of {options})"
    if type_name == 'integer':
        if 'minimum' in schema:
            string += f" (minimum: {schema['minimum']})"
        if 'maximum' in schema:
            string += f" (maximum: {schema['maximum']})"
    return string


def _is_array(schema):
    """
    Is a JSON Schema an array type?
    """
    if not isinstance(schema, dict):
        return False
    return schema.get('type') == 'array' or 'items' in schema or 'additionalItems' in schema


def _is_obj(schema):
    """
    Is a JSON Schema an object type?
    """
    if not isinstance(schema, dict):
        return False
    return schema.get('type') == 'object' or 'properties' in schema or 'additionalProperties' in schema
