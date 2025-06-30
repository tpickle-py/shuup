from django.template.loader import get_template
from django.views.generic import FormView

from shuup.core.models import ProductMode


class ProductOrderForm(FormView):
    template_name = "shuup/front/product/forms/product_order_form.jinja"
    engine = None
    priority = 0  # a greater number has precedence

    def __init__(self, request, context, product, language, **kwargs):
        self.request = request
        self.context = context
        self.product = product
        self.language = language
        super().__init__(**kwargs)

    def render(self):  # doccov: ignore
        # vars = self.get_context_data(context)
        if self.engine:
            template = self.engine.get_template(self.template_name)
        else:
            template = get_template(self.template_name)
        return template.render(self.context, request=self.request)

    def is_compatible(self):
        return False


class VariableVariationProductOrderForm(ProductOrderForm):
    def is_compatible(self):
        return self.product.mode == ProductMode.VARIABLE_VARIATION_PARENT


class SimpleVariationProductOrderForm(ProductOrderForm):
    def is_compatible(self):
        return self.product.mode == ProductMode.SIMPLE_VARIATION_PARENT


class SimpleProductOrderForm(ProductOrderForm):
    def is_compatible(self):
        return self.product.mode in [ProductMode.NORMAL, ProductMode.PACKAGE_PARENT]
