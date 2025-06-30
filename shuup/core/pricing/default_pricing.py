from django.utils.translation import ugettext_lazy as _

from shuup.core.models import ShopProduct
from shuup.core.pricing import PriceInfo, PricingModule


class DefaultPricingModule(PricingModule):
    identifier = "default_pricing"
    name = _("Default Pricing")

    def get_price_info(self, context, product, quantity=1):
        """
        Return a `PriceInfo` calculated from `ShopProduct.default_price`

        Since `ShopProduct.default_price` can be `None` it will
        be set to zero (0) if `None`.
        """
        shop = context.shop
        shop_product = ShopProduct.objects.get(product=product, shop=shop)

        default_price = shop_product.default_price_value or 0

        return PriceInfo(
            price=shop.create_price(default_price * quantity),
            base_price=shop.create_price(default_price * quantity),
            quantity=quantity,
        )
