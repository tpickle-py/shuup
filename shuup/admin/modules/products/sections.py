

from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import Section
from shuup.core.models import Order


class ProductOrdersSection(Section):
    identifier = "product_orders"
    name = _("Orders")
    icon = "fa-inbox"
    template = "shuup/admin/products/_product_orders.jinja"
    order = 1

    @classmethod
    def visible_for_object(cls, product, request=None):
        has_product_id = bool(product.pk)
        if not request:
            return has_product_id

        from shuup.admin.utils.permissions import has_permission

        return bool(has_product_id) and has_permission(
            request.user, "shop_product.edit"
        )

    @classmethod
    def get_context_data(cls, product, request=None):
        # TODO: restrict to first 100 orders - do pagination later
        return (
            Order.objects.valid().filter(lines__product_id=product.id).distinct()[:100]
        )
