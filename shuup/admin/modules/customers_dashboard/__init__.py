from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule

from .dashboard import get_active_customers_block


class CustomersDashboardModule(AdminModule):
    name = _("Customers Dashboard")

    def get_dashboard_blocks(self, request):
        yield get_active_customers_block(request)
