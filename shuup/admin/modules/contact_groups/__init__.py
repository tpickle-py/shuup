from django.utils.translation import gettext_lazy as _

from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.menu import CONTACTS_MENU_CATEGORY
from shuup.admin.utils.urls import admin_url, derive_model_url, get_edit_and_list_urls
from shuup.core.models import ContactGroup


class ContactGroupModule(AdminModule):
    name = _("Contact Groups")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:contact_group.list")

    def get_urls(self):
        return [
            admin_url(
                r"^contact_group/(?P<pk>\d+)/delete/$",
                "shuup.admin.modules.contact_groups.views.ContactGroupDeleteView",
                name="contact_group.delete",
            )
        ] + get_edit_and_list_urls(
            url_prefix="^contact_group",
            view_template="shuup.admin.modules.contact_groups.views.ContactGroup%sView",
            name_template="contact_group.%s",
        )

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-asterisk",
                url="shuup_admin:contact_group.list",
                category=CONTACTS_MENU_CATEGORY,
                ordering=2,
            ),
        ]

    def get_model_url(self, object, kind, shop=None):
        return derive_model_url(ContactGroup, "shuup_admin:contact_group", object, kind)
