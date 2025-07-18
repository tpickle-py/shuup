import decimal

from django.http import Http404

from shuup.core.models import ProductVariationResult, Supplier
from shuup.front.views.product import ProductDetailView
from shuup.utils.numbers import parse_simple_decimal


class ProductPriceView(ProductDetailView):
    template_name = "shuup/front/product/detail_order_section.jinja"

    def get_object(self, queryset=None):
        product = super().get_object(queryset)
        vars = self.get_variation_variables()
        return ProductVariationResult.resolve(product, vars) if vars else product

    def get_context_data(self, **kwargs):
        product = self.get_object()
        if not product:
            raise Http404
        context = super().get_context_data(**kwargs)
        shop_product = context["shop_product"]

        quantity = self._get_quantity(shop_product)
        if quantity is not None:
            context["quantity"] = context["product"].sales_unit.round(quantity)
        else:
            self.template_name = "shuup/front/product/detail_order_section_no_product.jinja"
            return context

        supplier_pk = self.request.GET.get("supplier")
        if supplier_pk:
            context["supplier"] = Supplier.objects.enabled(shop=shop_product.shop).filter(pk=int(supplier_pk)).first()
        else:
            context["supplier"] = shop_product.get_supplier(
                customer=self.request.customer,
                quantity=(quantity or shop_product.minimum_purchase_quantity),
            )

        is_orderable = shop_product.is_orderable(context["supplier"], self.request.customer, context["quantity"])
        if not context["product"] or not is_orderable:
            self.template_name = "shuup/front/product/detail_order_section_no_product.jinja"
            return context

        return context

    def _get_quantity(self, shop_product):
        quantity_text = self.request.GET.get("quantity", "")
        quantity = parse_simple_decimal(quantity_text, None)
        if quantity is None or quantity < 0:
            return None
        unit_type = self.request.GET.get("unitType", "internal")
        if unit_type == "internal":
            return quantity
        else:
            return shop_product.unit.from_display(decimal.Decimal(quantity))

    def get_variation_variables(self):
        return {int(k.split("_")[-1]): int(v) for (k, v) in self.request.GET.items() if k.startswith("var_")}

    def get(self, request, *args, **kwargs):
        # Skipping ProductPriceView.super for a reason.
        return super(ProductDetailView, self).get(request, *args, **kwargs)


def product_price(request):
    return ProductPriceView.as_view()(request, pk=request.GET["id"])
