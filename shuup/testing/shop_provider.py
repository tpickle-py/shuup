from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _

from shuup.core.models import Shop

SHOP_SESSION_KEY = "admin_shop"


class TestingAdminShopProvider:
    def get_shop(self, request):
        return Shop.objects.first()

    def set_shop(self, request, shop=None):
        if not request.user.is_staff:
            raise PermissionDenied(
                _("You must have the Access to Admin Panel permission.")
            )

        if shop:
            request.session[SHOP_SESSION_KEY] = shop.id
        else:
            self.unset_shop(request)

    def unset_shop(self, request):
        if SHOP_SESSION_KEY in request.session:
            del request.session[SHOP_SESSION_KEY]
