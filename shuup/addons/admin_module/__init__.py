from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import ADDONS_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url


class AddonModule(AdminModule):
    name = _("Addons")
    breadcrumbs_menu_entry = MenuEntry(text=name, url="shuup_admin:addon.list")

    def get_urls(self):
        return [
            admin_url(
                "^addons/$",
                "shuup.addons.admin_module.views.AddonListView",
                name="addon.list",
            ),
            admin_url(
                "^addons/add/$",
                "shuup.addons.admin_module.views.AddonUploadView",
                name="addon.upload",
            ),
            admin_url(
                "^addons/add/confirm/$",
                "shuup.addons.admin_module.views.AddonUploadConfirmView",
                name="addon.upload_confirm",
            ),
            admin_url(
                "^addons/reload/$",
                "shuup.addons.admin_module.views.ReloadView",
                name="addon.reload",
            ),
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=_("Addons"),
                icon="fa fa-puzzle-piece",
                url="shuup_admin:addon.list",
                category=ADDONS_MENU_CATEGORY,
            )
        ]
