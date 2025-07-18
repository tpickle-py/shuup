import logging

from django.utils.translation import gettext_lazy as _

from shuup.core.shop_provider import get_shop
from shuup.utils.django_compat import MiddlewareMixin
from shuup.xtheme import get_current_theme

log = logging.getLogger(__name__)


class XthemeMiddleware(MiddlewareMixin):
    """
    Handle Shuup specific tasks for each request and response.

    This middleware requires the ShuupMiddleware or some other that
    can set the current shop in the request
    """

    def process_request(self, request):
        shop = getattr(request, "shop", get_shop(request))
        theme = get_current_theme(shop)
        if theme:
            request.theme = theme
            theme.set_current()
        else:
            log.error((_("Shop '{}' has no active theme")).format(shop))
