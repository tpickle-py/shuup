from typing import Iterable

from django.contrib.auth.models import Group as PermissionGroup
from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import STOREFRONT_MENU_CATEGORY
from shuup.admin.utils.object_selector import get_object_selector_permission_name
from shuup.admin.utils.urls import derive_model_url, get_edit_and_list_urls


class PermissionGroupModule(AdminModule):
    name = _("Granular Permission Groups")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:permission_group.list")

    def get_urls(self):
        return get_edit_and_list_urls(
            url_prefix="^permission-groups",
            view_template="shuup.admin.modules.permission_groups.views.PermissionGroup%sView",
            name_template="permission_group.%s",
        )

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-users",
                url="shuup_admin:permission_group.list",
                category=STOREFRONT_MENU_CATEGORY,
                ordering=3,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(PermissionGroup, "shuup_admin:permission_group", object, kind)

    def get_extra_permissions(self) -> Iterable[str]:
        return [get_object_selector_permission_name(PermissionGroup)]

    def get_permissions_help_texts(self) -> Iterable[str]:
        return {
            get_object_selector_permission_name(PermissionGroup): _(
                "Allow the user to select permission group in admin."
            )
        }
