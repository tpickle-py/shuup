

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import SETTINGS_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url


class TestingAdminModule(AdminModule):
    def get_urls(self):
        return [
            admin_url(
                "^mocker/$",
                "shuup.testing.modules.mocker.mocker_view.MockerView",
                name="mocker",
            )
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text="Create Mock Objects",
                category=SETTINGS_MENU_CATEGORY,
                url="shuup_admin:mocker",
                icon="fa fa-star",
            )
        ]
