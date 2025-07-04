from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import STOREFRONT_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url


class StocksAdminModule(AdminModule):
    name = _("Stock management")

    def get_urls(self):
        return [
            admin_url(
                r"^adjust-stock/(?P<supplier_id>\d+)/(?P<product_id>\d+)/",
                "shuup.simple_supplier.admin_module.views.process_stock_adjustment",
                name="simple_supplier.stocks",
            ),
            admin_url(
                r"^alert-limit/(?P<supplier_id>\d+)/(?P<product_id>\d+)/",
                "shuup.simple_supplier.admin_module.views.process_alert_limit",
                name="simple_supplier.alert_limits",
            ),
            admin_url(
                r"^manage-stock/(?P<supplier_id>\d+)/(?P<product_id>\d+)/",
                "shuup.simple_supplier.admin_module.views.process_stock_managed",
                name="simple_supplier.stock_managed",
            ),
            admin_url(
                r"^stocks/",
                "shuup.simple_supplier.admin_module.views.StocksListView",
                name="simple_supplier.stocks",
            ),
            admin_url(
                r"^list-settings/",
                "shuup.admin.modules.settings.views.ListSettingsView",
                name="simple_supplier.list_settings",
            ),
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-cubes",
                url="shuup_admin:simple_supplier.stocks",
                category=STOREFRONT_MENU_CATEGORY,
                ordering=6,
            )
        ]
