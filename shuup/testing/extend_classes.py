from shuup.core.models import ProductMode
from shuup.front.forms.order_forms import ProductOrderForm


class DifferentProductOrderForm(ProductOrderForm):
    template_name = "shuup_testing/different_order_form.jinja"

    def is_compatible(self):
        return self.product.mode == ProductMode.SUBSCRIPTION
