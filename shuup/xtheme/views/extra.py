from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.http.response import HttpResponseNotFound
from django.utils.html import escape

from shuup.xtheme._theme import get_current_theme

_VIEW_CACHE = {}


def clear_view_cache(**kwargs):
    _VIEW_CACHE.clear()


setting_changed.connect(clear_view_cache, dispatch_uid="shuup.xtheme.views.extra.clear_view_cache")


def _get_view_by_name(theme, view_name):
    view = theme.get_view(view_name)
    if hasattr(view, "as_view"):  # Handle CBVs
        view = view.as_view()
    if view and not callable(view):
        raise ImproperlyConfigured(f"Error! View `{view!r}` is not callable.")
    return view


def get_view_by_name(theme, view_name):
    if not theme:
        return None
    cache_key = (theme.identifier, view_name)
    if cache_key not in _VIEW_CACHE:
        view = _get_view_by_name(theme, view_name)
        _VIEW_CACHE[cache_key] = view
    else:
        view = _VIEW_CACHE[cache_key]
    return view


def extra_view_dispatch(request, view):
    """
    Dispatch to an Xtheme extra view.

    :param request: A request.
    :type request: django.http.HttpRequest
    :param view: View name.
    :type view: str
    :return: A response of some kind.
    :rtype: django.http.HttpResponse
    """
    theme = getattr(request, "theme", None) or get_current_theme(request.shop)
    view_func = get_view_by_name(theme, view)
    if not view_func:
        msg = "Error! {}/{}: Not found.".format(
            getattr(theme, "identifier", None),
            escape(view),
        )
        return HttpResponseNotFound(msg)
    return view_func(request)
