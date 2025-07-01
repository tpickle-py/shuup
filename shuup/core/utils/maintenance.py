def maintenance_mode_exempt(view_func):
    """
    Make view ignore shop maintenance mode

    :param view_func: view attached to this decorator
    :return: view added with maintenance_mode_exempt attribute
    """
    view_func.maintenance_mode_exempt = True
    return view_func
