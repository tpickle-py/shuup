from importlib import import_module

import six
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

_LOAD_CACHE = {}


def load(specification, context_explanation="Load"):
    delimiter = ":" if ":" in specification else "."
    module_name, object_name = specification.rsplit(delimiter, 1)
    try:
        module = import_module(module_name)
    except ImportError as ie:  # pragma: no cover
        exc = ImproperlyConfigured(
            f"Error! {context_explanation}: Could not import module `{module_name!r}` to load `{object_name!r}` from. (`{ie!r}`)"
        )
        six.raise_from(exc, ie)

    obj = getattr(module, object_name, None)
    if obj is None:  # pragma: no cover
        raise ImproperlyConfigured(
            f"Error! {context_explanation}: Module `{module!r}` does not have a name `{object_name!r}`, or its value is None."
        )
    return obj


def clear_load_cache():
    _LOAD_CACHE.clear()


def cached_load(setting_name, default_value=None):
    if setting_name in _LOAD_CACHE:
        return _LOAD_CACHE[setting_name]
    setting_value = getattr(settings, setting_name, None)
    if setting_value is not None:
        value = load(setting_value)
    else:
        value = default_value
    _LOAD_CACHE[setting_name] = value
    return value
