

from django.utils.translation import ugettext_lazy as _

from shuup.admin.toolbar import Toolbar
from shuup.admin.utils.picotable import ChoicesFilter, Column, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import Shop, ShopStatus
from shuup.core.settings_provider import ShuupSettings


class ShopListView(PicotableListView):
    model = Shop
    default_columns = [
        Column(
            "logo",
            _("Logo"),
            display="logo",
            class_name="text-center",
            raw=True,
            ordering=1,
            sortable=False,
        ),
        Column(
            "name",
            _("Name"),
            sort_field="translations__name",
            display="name",
            filter_config=TextFilter(
                filter_field="translations__name", placeholder=_("Filter by name...")
            ),
        ),
        Column("domain", _("Domain")),
        Column("identifier", _("Identifier")),
        Column(
            "status",
            _("Status"),
            filter_config=ChoicesFilter(choices=ShopStatus.choices),
        ),
    ]
    toolbar_buttons_provider_key = "shop_list_toolbar_provider"
    mass_actions_provider_key = "shop_list_mass_actions_provider"

    def get_queryset(self):
        return Shop.objects.get_for_user(self.request.user)

    def get_toolbar(self):
        if ShuupSettings.get_setting("SHUUP_ENABLE_MULTIPLE_SHOPS"):
            return super().get_toolbar()
        else:
            return Toolbar.for_view(self)
