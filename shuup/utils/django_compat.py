try:
    from django.urls import (
        NoReverseMatch,
        Resolver404,
        URLPattern,
        URLResolver,
        clear_url_caches,
        get_callable,
        get_resolver,
        get_urlconf,
        resolve,
        reverse,
        reverse_lazy,
        set_urlconf,
    )
    from django.urls.resolvers import RegexPattern
except ImportError:
    from django.core.urlresolvers import (  # noqa (F401)
        NoReverseMatch,
        RegexURLPattern as RegexPattern,
        RegexURLResolver as URLResolver,
        Resolver404,
        clear_url_caches,
        get_callable,
        get_resolver,
        get_urlconf,
        resolve,
        reverse,
        reverse_lazy,
        set_urlconf,
    )

    URLPattern = RegexPattern


try:
    from django.utils.text import format_lazy
except ImportError:
    from django.utils.translation import string_concat as format_lazy  # noqa (F401)


try:
    from django.utils.encoding import force_bytes
    from django.utils.encoding import force_str as force_text
except ImportError:
    try:
        from django.utils.encoding import force_bytes, force_text
    except ImportError:
        from django.utils.text import force_bytes, force_text  # noqa (F401)


try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:

    class MiddlewareMixin(object):  # noqa (F811)
        pass


def is_anonymous(user):
    return user.is_anonymous


def is_authenticated(user):
    return user.is_authenticated


def get_middleware_classes():
    from django.conf import settings

    return settings.MIDDLEWARE
