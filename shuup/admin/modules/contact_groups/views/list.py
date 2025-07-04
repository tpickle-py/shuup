from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from shuup.admin.toolbar import NewActionButton, SettingsActionButton, Toolbar
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import ContactGroup


class ContactGroupListView(PicotableListView):
    model = ContactGroup
    default_columns = [
        Column(
            "name",
            _("Name"),
            sort_field="translations__name",
            display="name",
            filter_config=TextFilter(filter_field="translations__name", placeholder=_("Filter by name...")),
        ),
        Column("n_members", _("Number of Members")),
    ]
    toolbar_buttons_provider_key = "contact_group_list_toolbar_provider"
    mass_actions_provider_key = "contact_group_list_mass_actions_provider"

    def get_queryset(self):
        return ContactGroup.objects.all_except_defaults().annotate(n_members=Count("members"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            settings_button = SettingsActionButton.for_model(ContactGroup, return_url="contact_group")
        else:
            settings_button = None
        context["toolbar"] = Toolbar(
            [NewActionButton("shuup_admin:contact_group.new"), settings_button],
            view=self,
        )
        return context
