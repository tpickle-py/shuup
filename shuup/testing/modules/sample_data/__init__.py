import os

from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry, Notification
from shuup.admin.menu import SETTINGS_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url
from shuup.core.settings_provider import ShuupSettings
from shuup.testing.modules.sample_data import manager as sample_manager

SAMPLE_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SAMPLE_IMAGES_BASE_DIR = os.path.join(SAMPLE_BASE_DIR, "sample_data/images")


class SampleDataAdminModule(AdminModule):
    def get_urls(self):
        return [
            admin_url(
                "^sample_data/$",
                "shuup.testing.modules.sample_data.views.ConsolidateSampleObjectsView",
                name="sample_data",
            )
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text="Sample Data",
                category=SETTINGS_MENU_CATEGORY,
                url="shuup_admin:sample_data",
                icon="fa fa-star",
            )
        ]

    def get_required_permissions(self):
        return ("Access sample data module",)

    def get_notifications(self, request):
        """Injects a message to the user and also a notification"""
        # multi-shop not supported
        if not ShuupSettings.get_setting("SHUUP_ENABLE_MULTIPLE_SHOPS"):
            from shuup.admin.shop_provider import get_shop

            shop = get_shop(request)

            if sample_manager.has_installed_samples(shop):
                messages.warning(
                    request,
                    _("There is a sample data installed. Search `Sample Data` for more information."),
                )

                yield Notification(
                    _("There is a sample data installed. Click here to consolidate or delete them."),
                    title=_("Sample Data"),
                    kind="warning",
                    url="shuup_admin:sample_data",
                )
