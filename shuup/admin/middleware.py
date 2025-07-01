from shuup.admin.shop_provider import get_shop
from shuup.utils.django_compat import MiddlewareMixin


class ShuupAdminMiddleware(MiddlewareMixin):
    """
    Handle Shuup Admin specific tasks for each request and response.

    * Sets the current shop from the request
      ``request.shop`` : :class:`shuup.core.models.Shop`
          Currently active Shop.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # we only care about Shuup Admin requests
        if request.resolver_match.app_name == "shuup_admin":
            shop = get_shop(request)
            if shop:
                request.shop = shop
