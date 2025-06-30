# -*- coding: utf-8 -*-
try:
    from . import _version
except ImportError:
    _version = None

__version__ = getattr(_version, "__version__", "dev")
