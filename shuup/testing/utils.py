import inspect
from functools import wraps

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.test import override_settings
from django.utils.module_loading import import_string
from django.utils.translation import activate, get_language

from shuup.admin import shop_provider
from shuup.utils.django_compat import RegexPattern, URLResolver, get_middleware_classes, set_urlconf


def apply_request_middleware(request, **attrs):
    """
    Apply all the `process_request` capable middleware configured
    into the given request.

    :param request: The request to massage.
    :type request: django.http.HttpRequest
    :param attrs: Additional attributes to set after massage.
    :type attrs: dict
    :return: The same request, massaged in-place.
    :rtype: django.http.HttpRequest
    """
    for middleware_path in get_middleware_classes():
        mw_class = import_string(middleware_path)
        current_language = get_language()

        try:
            mw_instance = mw_class()
        except MiddlewareNotUsed:
            continue

        for key, value in attrs.items():
            setattr(request, key, value)

        if hasattr(mw_instance, "process_request"):
            mw_instance.process_request(request)

        activate(current_language)

    assert request.shop

    if not attrs.get("skip_session", False):
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        if mod.__name__.startswith("shuup_tests.admin"):
            shop_provider.set_shop(request, request.shop)

    return request


def apply_view_middleware(request):
    """
    Apply all the `process_view` capable middleware configured
    into the given request.

    The logic is roughly copied from
    django.core.handlers.base.BaseHandler.get_response

    :param request: The request to massage.
    :type request: django.http.HttpRequest
    :return: The same request, massaged in-place.
    :rtype: django.http.HttpRequest
    """
    urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
    set_urlconf(urlconf)

    resolver = URLResolver(RegexPattern(r"^/"), urlconf)
    resolver_match = resolver.resolve(request.path_info)
    callback, callback_args, callback_kwargs = resolver_match
    request.resolver_match = resolver_match

    for middleware_path in get_middleware_classes():
        mw_class = import_string(middleware_path)
        try:
            mw_instance = mw_class()
        except MiddlewareNotUsed:
            continue

        if hasattr(mw_instance, "process_view"):
            mw_instance.process_view(request, callback, callback_args, callback_kwargs)

    return request


def disable_weak_password_middleware(test_func):
    """
    Decorator to disable weak password middleware for tests that don't check password complexity.

    This decorator temporarily removes the weak password middleware from Django's
    MIDDLEWARE setting during test execution, preventing password complexity
    validation from interfering with tests that focus on other functionality.

    Usage:
        @disable_weak_password_middleware
        def test_user_creation(self):
            # Test user creation without password complexity validation
            pass

    Args:
        test_func: The test function to decorate

    Returns:
        Wrapped test function with middleware disabled
    """

    @wraps(test_func)
    def wrapper(*args, **kwargs):
        # Get current middleware and filter out weak password middleware
        current_middleware = list(getattr(settings, "MIDDLEWARE", []))
        filtered_middleware = [
            mw
            for mw in current_middleware
            if not any(keyword in mw.lower() for keyword in ["weak_password", "weakpassword", "password_middleware"])
        ]

        # Also disable any password validation settings
        password_settings_override = {
            "MIDDLEWARE": filtered_middleware,
            "AUTH_PASSWORD_VALIDATORS": [],  # Disable Django's built-in password validation
        }

        # Use override_settings to temporarily disable the middleware and validators
        with override_settings(**password_settings_override):
            return test_func(*args, **kwargs)

    return wrapper


def apply_all_middleware(request, **attrs):
    """
    Apply all the `process_request` and `process_view` capable
    middleware configured into the given request.

    :param request: The request to massage.
    :type request: django.http.HttpRequest
    :param attrs: Additional attributes to set to the request after massage.
    :type attrs: dict
    :return: The same request, massaged in-place.
    :rtype: django.http.HttpRequest
    """
    request = apply_view_middleware(apply_request_middleware(request))
    for key, value in attrs.items():
        setattr(request, key, value)
    return request
