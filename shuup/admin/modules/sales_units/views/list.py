

from django.utils.translation import ugettext_lazy as _

from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import DisplayUnit, SalesUnit


class UnitListView(PicotableListView):
    default_columns = [
        Column(
            "name",
            _("Name"),
            sort_field="translations__name",
            display="name",
            filter_config=TextFilter(
                filter_field="translations__name", placeholder=_("Filter by name...")
            ),
        ),
        Column(
            "symbol", _("Symbol"), sort_field="translations__symbol", display="symbol"
        ),
        Column("decimals", _("Allowed decimals")),
    ]
    toolbar_buttons_provider_key = "sales_unit_list_toolbar_provider"
    mass_actions_provider_key = "sales_unit_list_mass_actions_provider"

    def get_queryset(self):
        return self.model.objects.all()


class SalesUnitListView(UnitListView):
    model = SalesUnit


class DisplayUnitListView(UnitListView):
    model = DisplayUnit
