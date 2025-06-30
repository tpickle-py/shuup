
"""
Compatibility module for Django and other library version differences.
"""

# Django compatibility
try:
    from django.utils.encoding import python_2_unicode_compatible  # type: ignore  # noqa: I001
except ImportError:
    # In Django 4.0+, this decorator is no longer needed since Python 2 support was dropped
    def python_2_unicode_compatible(cls):
        return cls


# Django.utils.six was removed in Django 4.0
try:
    from django.utils import six  # type: ignore  # noqa: I001
except ImportError:
    # Django removed six in 4.0, use the external package
    pass

# Jinja2 compatibility
try:
    from jinja2.utils import contextfunction  # type: ignore  # noqa: I001
except ImportError:
    # In Jinja2 3.0+, contextfunction was replaced with pass_context
    try:
        from jinja2 import pass_context as contextfunction
    except ImportError:
        # Fallback for older versions
        def contextfunction(f):
            return f


try:
    from jinja2 import contextfilter  # type: ignore  # noqa: I001
except ImportError:
    # In Jinja2 3.0+, contextfilter was replaced with pass_context
    try:
        from jinja2 import pass_context as contextfilter
    except ImportError:
        # Fallback for older versions
        def contextfilter(f):
            return f

__all__ = [
    "python_2_unicode_compatible",
    "six",
    "contextfunction",
    "contextfilter",
]
