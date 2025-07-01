import math


def float_wrap(value, func):
    try:
        return func(float(value))
    except Exception:
        return None


def extend_sqlite_functions(connection=None, **kwargs):
    """
    Extends SQLite with trigonometry functions
    """
    if connection and connection.vendor == "sqlite":
        connection.connection.create_function("sin", 1, lambda x: float_wrap(x, math.sin))
        connection.connection.create_function("cos", 1, lambda x: float_wrap(x, math.cos))
        connection.connection.create_function("acos", 1, lambda x: float_wrap(x, math.acos))
        connection.connection.create_function("degrees", 1, lambda x: float_wrap(x, math.degrees))
        connection.connection.create_function("radians", 1, lambda x: float_wrap(x, math.radians))
