def update_dict_recursive(source: dict, updated_data: dict):
    """Recursively updates a dictionary with values from another dictionary"""
    for key, value in updated_data.items():
        if isinstance(value, dict) and key in source and isinstance(source[key], dict):
            update_dict_recursive(source[key], updated_data[key])
        else:
            source[key] = updated_data[key]
