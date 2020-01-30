"""
Generate API documentation from an API object.
"""

# TODO table of contents
# TODO schema titles and descriptions


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
        # Table of contents
        fd.write(f'## Table of Contents\n\n')
        fd.write(f'[Methods](#methods) ({len(api.methods)} total)\n')
        for (_id, meth) in api.methods.items():
            deprec_reason = meth.get('deprecated')
            if deprec_reason:
                fd.write(f'* ~~[{meth["name"]}](#{meth["name"]})~~\n')
            else:
                fd.write(f'* [{meth["name"]}](#{meth["name"]})\n')
        fd.write('\n')
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
                    fd.write(f'**Parameters:**\n')
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
                    fd.write(f'**Result:**\n')
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
    print(f'Wrote docs to {path}')
    return path


def _format_keyval(key, val, parent, obj_indent):
    """
    Return a special format for a key-val entry in a JSON object.
    """
    if key == '$id' or key == 'type' or key == '$ref':
        return False
    elif key == 'required':
        prop_names = ', '.join(val)
        return f'Required fields: **{prop_names}**'
    elif key == 'properties':
        return 'Properties:\n' + _format_obj_props(val, obj_indent + 1, parent)
    elif key == 'additionalProperties':
        if val is False:
            return 'No extra properties are allowed'
    elif key == 'items':
        return f'**items**:\n{_format_generic_json(val, obj_indent + 1)}'


def _format_obj_props(props, indent, parent):
    string = ''
    for (prop, typ) in props.items():
        string += ('  ' * indent) + f'* `"{prop}"` – {_format_generic_json(typ, indent + 1, prop, parent)}\n'
    return string


def _format_obj_prefix(schema, indent, parent, prop_name):
    """
    Create a string prefix (possibly None) for a schema object.
    """
    if not isinstance(schema, dict):
        return None
    string = ''
    if parent:
        required = set(parent.get('required', set()))
        if prop_name and prop_name in required:
            string += 'required '
    if schema.get('$ref'):
        ref = schema['$ref']
        return f"[{ref}]({ref})"
    if _is_obj(schema):
        string = 'JSON object'
        return string
    if _is_array(schema):
        return 'JSON array'
    typ = schema.get('type')
    if typ:
        return typ


def _format_generic_json(data, obj_indent=0, prop_name=None, parent=None):
    """
    Render any JSON serializable data structure as bulleted markdown.
    """
    string = ''
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
                string += ('  ' * obj_indent) + '* ' + keyval + '\n'
                continue
            string += ('  ' * obj_indent) + f'* **{key}** – '
            if isinstance(val, dict):
                if not val:
                    string += 'empty object\n'
                else:
                    string += f'object of:\n{sub}'
            elif isinstance(val, list):
                if not val:
                    string += f'empty array\n'
                else:
                    string += f'array of:\n{sub}'
            else:
                string += f'{sub}\n'
        return string
    elif isinstance(data, list):
        for val in data:
            sub = _format_generic_json(val, obj_indent + 1, prop_name, parent)
            string += ('  ' * obj_indent) + '1. '
            if isinstance(val, dict):
                if val:
                    string += f'object of:\n{sub}'
                else:
                    string += 'empty object\n'
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
    result_schema = method.get('result_schema')
    meth_title = f'{meth_name}({_format_type_short(params_schema)})'
    deprec_reason = method.get('deprecated')
    if result_schema:
        meth_title += f' ⇒ {_format_type_short(result_schema)}'
    if deprec_reason:
        meth_title = '~~' + meth_title + '~~'
    return meth_title
    pass


# def _format_type(schema):
#     type_name = schema.get('type')
#     if type_name == 'object' or 'properties' in schema or 'additionalProperties' in schema:
#         return _format_obj_type(schema)
#     elif type_name == 'array' or 'items' in schema or 'additionalItems' in schema:
#         return _format_arr_type(schema)
#     else:
#         return ''


def _format_arr_type(schema, indent=0):
    string = "**JSON array**\n\n"
    item_type_strs = _format_arr_items(schema)
    if item_type_strs:
        string = "**JSON array** where:\n\n"
        string += item_type_strs
        string += "\n"
    return string


def _format_arr_items(schema, indent=0):
    items = schema.get('items')
    string = ""
    if isinstance(items, list):
        item_type_strs = [_format_type_short(t) for t in items]
        if item_type_strs:
            for (idx, t) in enumerate(item_type_strs):
                string += (" " * indent) + f"* Item {idx} must be {t}\n"
    elif items:
        typ = _format_type_short(items)
        string += (" " * indent) + f"* Items must be {typ}\n"
    addl_items = schema.get('additionalItems')
    if addl_items is False:
        string += (" " * indent) + "* No extra items are allowed\n"
    elif addl_items:
        string += (" " * indent) + f"* Additional items must be: {_format_type_short(addl_items)}\n"
    return string


# def _format_obj_type(schema):
#     required = set(schema.get('required', []))
#     props = schema.get('properties')
#     string = "**JSON object** with properties:\n\n"
#     if props:
#         for (prop_name, prop_type) in props.items():
#             is_required = prop_name in required
#             string += _format_obj_field(prop_name, prop_type, is_required, indent=0)
#         string += "\n"
#     else:
#         string = "**JSON object**\n\n"
#     if schema.get('additionalProperties') is False:
#         string += "No extra properties are allowed\n\n"
#     return string


# def _format_obj_field(prop_name, prop_type, is_required, indent=0):
#     """
#     Create an unordered list string for a property name and value inside an object type.
#     """
#     string = ("  " * indent) + "* "
#     desc = prop_type.get('description')
#     req_text = "required" if is_required else "optional"
#     desc = prop_type.get('description')
#     desc = '- ' + desc if desc else ''
#     type_name = prop_type.get('type')
#     string += f'`"{prop_name}"` – {req_text}'
#     if type_name == 'object':   # TODO _is_obj()
#         string += f' object with the following properties:\n'
#         props = prop_type.get('properties')
#         required = set(prop_type.get('required', []))
#         for (prop_name, prop_type) in props.items():
#             is_required = prop_name in required
#             string += _format_obj_field(prop_name, prop_type, is_required, indent=indent + 1)
#     elif _is_array(prop_type):
#         string += f' array where\n'
#         string += _format_arr_items(prop_type, indent + 1)
#     else:
#         string += f' {_format_type_short(prop_type)}\n'
#     return string


def _format_type_short(typ):
    if typ == {}:
        return 'any type'
    if not typ:
        return ''
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
        if 'minimum' in typ:
            string += f" (minimum: {typ['minimum']})"
        if 'maximum' in typ:
            string += f" (maximum: {typ['maximum']})"
    return string


def _is_array(typ):
    if not isinstance(typ, dict):
        return False
    return typ.get('type') == 'array' or 'items' in typ or 'additionalItems' in typ


def _is_obj(typ):
    if not isinstance(typ, dict):
        return False
    return typ.get('type') == 'object' or 'properties' in typ or 'additionalProperties' in typ


def _format_obj_type(schema, indent=0):
    """
    Within a bulleted list, return special object type formatting
    """
    # required = set(schema.get('required', set()))
    string = 'JSON object of:\n'
    for (key, val) in schema.get('properties', {}).items():
        string += ('  ' * indent) + f'* `"{key}"` – val todo'
    return string
