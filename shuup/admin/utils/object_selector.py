

def get_object_selector_permission_name(model):
    """
    Returns the object selector permission name for the given model
    """
    return f"{model._meta.model_name}.object_selector"
