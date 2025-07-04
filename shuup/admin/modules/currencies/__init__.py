from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import STOREFRONT_MENU_CATEGORY
from shuup.admin.utils.urls import derive_model_url, get_edit_and_list_urls
from shuup.core.models import Currency


class CurrencyModule(AdminModule):
    name = _("Currencies")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:currency.list")

    def get_urls(self):
        return get_edit_and_list_urls(
            url_prefix="^currencies",
            view_template="shuup.admin.modules.currencies.views.Currency%sView",
            name_template="currency.%s",
        )

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-money",
                url="shuup_admin:currency.list",
                category=STOREFRONT_MENU_CATEGORY,
                ordering=2,
            ),
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(Currency, "shuup_admin:currency", object, kind)
