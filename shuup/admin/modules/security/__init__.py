"""
Security administration module for Shuup.

This module provides administrative interfaces for managing password security,
user security analysis, and security configuration.
"""

from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import SETTINGS_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url


class SecurityAdminModule(AdminModule):
    """
    Admin module for security management.

    Provides interfaces for:
    - Security dashboard with metrics
    - Weak password user management
    - Bulk security operations
    - Security configuration
    """

    name = _("Security")
    breadcrumbs_menu_entry = MenuEntry(name, "shuup_admin:security.dashboard")

    def get_urls(self):
        return [
            admin_url(
                r"^security/$",
                "shuup.admin.modules.security.views.dashboard.SecurityDashboardView",
                name="security.dashboard",
            ),
            admin_url(
                r"^security/weak-passwords/$",
                "shuup.admin.modules.security.views.weak_passwords.WeakPasswordListView",
                name="security.weak_passwords",
            ),
            admin_url(
                r"^security/weak-passwords/(?P<pk>\d+)/$",
                "shuup.admin.modules.security.views.weak_passwords.WeakPasswordDetailView",
                name="security.weak_password_detail",
            ),
            admin_url(
                r"^security/bulk-actions/$",
                "shuup.admin.modules.security.views.weak_passwords.BulkSecurityActionView",
                name="security.bulk_actions",
            ),
            admin_url(
                r"^security/settings/$",
                "shuup.admin.modules.security.views.settings.SecuritySettingsView",
                name="security.settings",
            ),
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=_("Security Dashboard"),
                icon="fa fa-shield",
                url="shuup_admin:security.dashboard",
                category=SETTINGS_MENU_CATEGORY,
                ordering=1,
            ),
        ]

    def get_help_blocks(self, request, kind):
        if kind == "setup":
            yield {
                "title": _("Password Security"),
                "text": _(
                    "Monitor and manage password security across your platform. "
                    "Identify users with weak passwords and take proactive security measures."
                ),
                "actions": [
                    {
                        "text": _("Security Dashboard"),
                        "url": "shuup_admin:security.dashboard",
                    }
                ],
            }
