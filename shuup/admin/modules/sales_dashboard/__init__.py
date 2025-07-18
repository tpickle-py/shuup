from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule
from shuup.admin.currencybound import CurrencyBound


class SalesDashboardModule(CurrencyBound, AdminModule):
    name = _("Sales Dashboard")

    def get_dashboard_blocks(self, request):
        import shuup.admin.modules.sales_dashboard.dashboard as dashboard

        currency = self.currency
        if not currency:
            shop = request.shop
            currency = shop.currency

        yield dashboard.get_sales_of_the_day_block(request, currency)
        yield dashboard.get_lifetime_sales_block(request, currency)
        yield dashboard.get_avg_purchase_size_block(request, currency)
        yield dashboard.get_open_orders_block(request, currency)
        yield dashboard.get_order_value_chart_dashboard_block(request, currency)
        yield dashboard.get_shop_overview_block(request, currency)
        yield dashboard.get_recent_orders_block(request, currency)
