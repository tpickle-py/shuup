from django.utils.translation import gettext_lazy as _

from shuup.admin.base import Section
from shuup.admin.shop_provider import get_shop
from shuup.admin.supplier_provider import get_supplier
from shuup.campaigns.models import BasketCampaign
from shuup.core.models import ShopProduct


class ProductCampaignsSection(Section):
    identifier = "product_campaigns"
    name = _("Active Basket Campaigns")
    icon = "fa-bullhorn"
    template = "shuup/campaigns/admin/_product_campaigns.jinja"

    @classmethod
    def visible_for_object(cls, product, request=None):
        return bool(product.pk)

    @classmethod
    def get_context_data(cls, product, request=None):
        ctx = {}
        shop = get_shop(request)
        try:
            shop_product = product.get_shop_instance(shop)
            basket_campaigns = BasketCampaign.get_for_product(shop_product)
            supplier = get_supplier(request)
            if supplier:
                basket_campaigns = basket_campaigns.filter(supplier=supplier)

            ctx[shop] = {"basket_campaigns": basket_campaigns}
            return ctx
        except ShopProduct.DoesNotExist:
            return ctx
