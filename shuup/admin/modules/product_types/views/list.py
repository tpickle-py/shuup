from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import ProductType


class ProductTypeListView(PicotableListView):
    model = ProductType
    default_columns = [
        Column(
            "name",
            _("Name"),
            sort_field="translations__name",
            display="name",
            filter_config=TextFilter(filter_field="translations__name", placeholder=_("Filter by name...")),
        ),
        Column("n_attributes", _("Number of Attributes")),
    ]
    toolbar_buttons_provider_key = "product_type_list_toolbar_provider"
    mass_actions_provider_key = "product_type_list_mass_actions_provider"

    def get_queryset(self):
        return ProductType.objects.all().annotate(n_attributes=Count("attributes"))
