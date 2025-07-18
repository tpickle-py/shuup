from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import REPORTS_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url
from shuup.reports.report import get_report_classes


class ReportsAdminModule(AdminModule):
    name = _("Reports")
    breadcrumbs_menu_entry = MenuEntry(text=name, url="shuup_admin:reports.list")

    def get_urls(self):
        return [
            admin_url(
                "^reports/$",
                "shuup.reports.admin_module.views.ReportView",
                name="reports.list",
            )
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-image",
                url="shuup_admin:reports.list",
                category=REPORTS_MENU_CATEGORY,
            )
        ]

    def get_extra_permissions(self):
        report_identifiers = set()
        for report_class in get_report_classes():
            report_identifiers.add(report_class)
        return report_identifiers
