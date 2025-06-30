from django.utils.translation import ugettext_lazy as _

from shuup.admin.dashboard import DashboardNumberBlock
from shuup.core.models import Order


def get_active_customers_block(request):
    shop = request.shop
    customer_ids = set(
        Order.objects.filter(shop=shop).since(30).values_list("customer_id", flat=True)
    )

    return DashboardNumberBlock(
        id="active_customers_count",
        color="blue",
        title=_("Active customers"),
        value=len(customer_ids),
        icon="fa fa-history",
        subtitle=_("Based on orders within 30 days"),
    )
