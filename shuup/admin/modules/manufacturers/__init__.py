from typing import Iterable

from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import STOREFRONT_MENU_CATEGORY
from shuup.admin.utils.object_selector import get_object_selector_permission_name
from shuup.admin.utils.urls import admin_url, derive_model_url, get_edit_and_list_urls
from shuup.core.models import Manufacturer


class ManufacturerModule(AdminModule):
    name = _("Manufacturers")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:manufacturer.list")

    def get_urls(self):
        return [
            admin_url(
                r"^manufacturer/(?P<pk>\d+)/delete/$",
                "shuup.admin.modules.manufacturers.views.ManufacturerDeleteView",
                name="manufacturer.delete",
            )
        ] + get_edit_and_list_urls(
            url_prefix="^manufacturers",
            view_template="shuup.admin.modules.manufacturers.views.Manufacturer%sView",
            name_template="manufacturer.%s",
        )

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=_("Manufacturers"),
                icon="fa fa-building",
                url="shuup_admin:manufacturer.list",
                category=STOREFRONT_MENU_CATEGORY,
                ordering=4,
            ),
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(Manufacturer, "shuup_admin:manufacturer", object, kind)

    def get_extra_permissions(self) -> Iterable[str]:
        return [get_object_selector_permission_name(Manufacturer)]

    def get_permissions_help_texts(self) -> Iterable[str]:
        return {
            get_object_selector_permission_name(Manufacturer): _("Allow the user to select manufacturers in admin.")
        }
