

def find_keys(data: dict, keys):
    """
    Find nested values for all nested keys that match `key.
    """
    for each_key, val in data.items():
        if each_key in keys:
            yield val
        if isinstance(val, dict):
            for result in find_keys(val, keys):
                yield result
