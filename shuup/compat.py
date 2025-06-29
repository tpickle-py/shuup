# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Commerce Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.

"""
Compatibility module for Django and other library version differences.
"""

# Django compatibility
try:
    from django.utils.encoding import python_2_unicode_compatible
except ImportError:
    # In Django 4.0+, this decorator is no longer needed since Python 2 support was dropped
    def python_2_unicode_compatible(cls):
        return cls

# Django.utils.six was removed in Django 4.0
try:
    from django.utils import six
except ImportError:
    # Django removed six in 4.0, use the external package
    import six

# Jinja2 compatibility
try:
    from jinja2.utils import contextfunction
except ImportError:
    # In Jinja2 3.0+, contextfunction was replaced with pass_context
    try:
        from jinja2 import pass_context as contextfunction
    except ImportError:
        # Fallback for older versions
        def contextfunction(f):
            return f

try:
    from jinja2 import contextfilter
except ImportError:
    # In Jinja2 3.0+, contextfilter was replaced with pass_context
    try:
        from jinja2 import pass_context as contextfilter
    except ImportError:
        # Fallback for older versions
        def contextfilter(f):
            return f
