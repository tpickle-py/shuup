from django.contrib.auth.models import Group as PermissionGroup
from django.utils.translation import gettext_lazy as _

from shuup.admin.toolbar import NewActionButton, SettingsActionButton, Toolbar
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import PicotableListView


class PermissionGroupListView(PicotableListView):
    model = PermissionGroup
    default_columns = [
        Column(
            "name",
            _("Name"),
            sort_field="name",
            display="name",
            filter_config=TextFilter(filter_field="name", placeholder=_("Filter by name...")),
        ),
    ]
    toolbar_buttons_provider_key = "permission_group_list_toolbar_provider"
    mass_actions_provider_key = "permission_group_list_mass_actions_provider"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Granular Permission Groups")
        if self.request.user.is_superuser:
            settings_button = SettingsActionButton.for_model(self.model, return_url="permission_group")
        else:
            settings_button = None
        context["toolbar"] = Toolbar(
            [
                NewActionButton(
                    "shuup_admin:permission_group.new",
                    text=_("Create new Permission Group"),
                ),
                settings_button,
            ],
            view=self,
        )
        return context
