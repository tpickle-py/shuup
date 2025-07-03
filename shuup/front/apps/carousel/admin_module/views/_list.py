from django.utils.translation import gettext_lazy as _

from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.front.apps.carousel.models import Carousel


class CarouselListView(PicotableListView):
    model = Carousel
    default_columns = [
        Column(
            "name",
            _("Name"),
            sort_field="name",
            display="name",
            filter_config=TextFilter(filter_field="name", placeholder=_("Filter by name...")),
        ),
    ]

    def get_queryset(self):
        return super().get_queryset().filter(shops=get_shop(self.request))
