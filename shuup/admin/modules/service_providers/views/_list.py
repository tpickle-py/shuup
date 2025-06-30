

from django.utils.translation import ugettext_lazy as _

from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import ServiceProvider


class ServiceProviderListView(PicotableListView):
    model = ServiceProvider
    default_columns = [
        Column(
            "name",
            _("Name"),
            sort_field="base_translations__name",
            filter_config=TextFilter(
                filter_field="base_translations__name",
                placeholder=_("Filter by name..."),
            ),
        ),
        Column("type", _("Type"), display="get_type_display", sortable=False),
    ]
    toolbar_buttons_provider_key = "service_provider_list_toolbar_provider"
    mass_actions_provider_key = "service_provider_mass_actions_provider"

    def get_type_display(self, instance):
        return instance._meta.verbose_name.capitalize()

    def get_object_abstract(self, instance, item):
        return [
            {"text": f"{instance}", "class": "header"},
            {"text": self.get_type_display(instance)},
        ]
