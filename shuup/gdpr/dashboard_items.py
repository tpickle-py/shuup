from django.utils.translation import gettext_lazy as _

from shuup.front.utils.dashboard import DashboardItem


class GDPRDashboardItem(DashboardItem):
    template_name = None
    title = _("My Data")
    icon = "fa fa-shield"
    _url = "shuup:gdpr_customer_dashboard"
    description = _("Customer data")

    def show_on_dashboard(self):
        return False
