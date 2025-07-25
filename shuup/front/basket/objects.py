from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from shuup import configuration
from shuup.core.basket.objects import BaseBasket as Basket
from shuup.front.checkout.methods import PAYMENT_METHOD_REQUIRED_CONFIG_KEY, SHIPPING_METHOD_REQUIRED_CONFIG_KEY


class BaseBasket(Basket):
    def __init__(self, request, basket_name="basket", shop=None, **kwargs):
        super().__init__(request, basket_name, shop)
        self.basket_name = basket_name

    def get_methods_validation_errors(self):
        shipping_methods = self.get_available_shipping_methods()
        payment_methods = self.get_available_payment_methods()

        advice = _("Try to remove some products from the basket and order them separately.")

        if (
            self.has_shippable_lines()
            and not shipping_methods
            and configuration.get(self.shop, SHIPPING_METHOD_REQUIRED_CONFIG_KEY, True)
        ):
            msg = _("Products in basket can't be shipped together. %s")
            yield ValidationError(msg % advice, code="no_common_shipping")

        if not payment_methods and configuration.get(self.shop, PAYMENT_METHOD_REQUIRED_CONFIG_KEY, True):
            msg = _("Products in basket have no common payment method. %s")
            yield ValidationError(msg % advice, code="no_common_payment")
