from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import SETTINGS_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url


class SettingsModule(AdminModule):
    name = _("System Settings")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:settings.list")

    def get_urls(self):
        return [
            admin_url(
                "^settings/$",
                "shuup.admin.modules.settings.views.SystemSettingsView",
                name="settings.list",
            )
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-home",
                url="shuup_admin:settings.list",
                category=SETTINGS_MENU_CATEGORY,
                ordering=4,
            )
        ]
