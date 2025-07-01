from typing import Iterable

from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import STOREFRONT_MENU_CATEGORY
from shuup.admin.utils.object_selector import get_object_selector_permission_name
from shuup.admin.utils.urls import admin_url, derive_model_url, get_edit_and_list_urls
from shuup.core.models import Attribute


class AttributeModule(AdminModule):
    name = _("Attributes")
    breadcrumbs_menu_entry = MenuEntry(text=name, url="shuup_admin:attribute.list")

    def get_urls(self):
        return [
            admin_url(
                r"^attributes/(?P<pk>\d+)/delete/$",
                "shuup.admin.modules.attributes.views.edit.AttributeDeleteView",
                name="attribute.delete",
            )
        ] + get_edit_and_list_urls(
            url_prefix="^attributes",
            view_template="shuup.admin.modules.attributes.views.Attribute%sView",
            name_template="attribute.%s",
        )

    def get_menu_category_icons(self):
        return {self.name: "fa fa-tags"}

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=_("Attributes"),
                icon="fa fa-tags",
                url="shuup_admin:attribute.list",
                category=STOREFRONT_MENU_CATEGORY,
                ordering=8,
            )
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(Attribute, "shuup_admin:attribute", object, kind)

    def get_extra_permissions(self) -> Iterable[str]:
        return [get_object_selector_permission_name(Attribute)]

    def get_permissions_help_texts(self) -> Iterable[str]:
        return {get_object_selector_permission_name(Attribute): _("Allow the user to select attributes in admin.")}
