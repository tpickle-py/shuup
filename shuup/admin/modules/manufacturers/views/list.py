from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import Manufacturer


class ManufacturerListView(PicotableListView):
    model = Manufacturer
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
            sort_field="name",
            display="name",
            filter_config=TextFilter(filter_field="name", placeholder=_("Filter by name...")),
        ),
    ]
    toolbar_buttons_provider_key = "manufacturer_list_toolbar_provider"
    mass_actions_provider_key = "manufacturer_list_mass_actions_provider"

    def get_queryset(self):
        return Manufacturer.objects.filter(Q(shops=get_shop(self.request)) | Q(shops__isnull=True))
