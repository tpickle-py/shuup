from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from shuup.admin.shop_provider import get_shop
from shuup.admin.supplier_provider import get_supplier
from shuup.admin.utils.urls import get_model_url
from shuup.core.models import ShopProduct
from shuup.core.specs.product_kind import DefaultProductKindSpec, get_product_kind_specs
from shuup.utils.importing import cached_load


class ProductCopyView(DetailView):
    model = ShopProduct
    context_object_name = "product"
    product_listing_names = [DefaultProductKindSpec.admin_listing_name]

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(
                shop=get_shop(self.request),
                product__kind__in=self.get_listing_product_kinds_values(),
            )
        )

        supplier = get_supplier(self.request)
        if supplier:
            qs = qs.filter(suppliers=supplier)

        return qs

    def get_listing_product_kinds_values(self):
        return [
            product_kind_spec.value
            for product_kind_spec in get_product_kind_specs()
            if product_kind_spec.admin_listing_name in self.product_listing_names
        ]

    def get_success_url(self, copied_shop_product: ShopProduct):
        return get_model_url(copied_shop_product, shop=get_shop(self.request))

    def get(self, request, *args, **kwargs):
        shop_product = self.get_object()
        current_supplier = None if request.user.is_superuser else get_supplier(request)
        cloner = cached_load("SHUUP_ADMIN_PRODUCT_CLONER")(request.shop, current_supplier)
        copied_shop_product = cloner.clone_product(shop_product=shop_product)
        messages.success(
            request,
            _(f"{copied_shop_product.product} was successfully copied"),
        )
        return HttpResponseRedirect(self.get_success_url(copied_shop_product))
