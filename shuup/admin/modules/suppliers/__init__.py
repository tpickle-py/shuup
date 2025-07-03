from typing import Iterable

from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import STOREFRONT_MENU_CATEGORY
from shuup.admin.utils.object_selector import get_object_selector_permission_name
from shuup.admin.utils.urls import admin_url, derive_model_url, get_edit_and_list_urls
from shuup.core.models import Supplier


class SupplierModule(AdminModule):
    name = _("Suppliers")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:supplier.list")

    def get_urls(self):
        return get_edit_and_list_urls(
            url_prefix="^suppliers",
            view_template="shuup.admin.modules.suppliers.views.Supplier%sView",
            name_template="supplier.%s",
        ) + [
            admin_url(
                r"^suppliers/delete/(?P<pk>\d+)/$",
                "shuup.admin.modules.suppliers.views.SupplierDeleteView",
                name="supplier.delete",
                permissions=("supplier.delete",),
            ),
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=_("Suppliers"),
                icon="fa fa-truck",
                url="shuup_admin:supplier.list",
                category=STOREFRONT_MENU_CATEGORY,
                ordering=7,
            ),
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(Supplier, "shuup_admin:supplier", object, kind)

    def get_extra_permissions(self) -> Iterable[str]:
        return [get_object_selector_permission_name(Supplier)]

    def get_permissions_help_texts(self) -> Iterable[str]:
        return {get_object_selector_permission_name(Supplier): _("Allow the user to select suppliers in admin.")}
