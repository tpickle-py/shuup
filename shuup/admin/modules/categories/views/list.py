from django.utils.translation import gettext_lazy as _

from shuup.admin.shop_provider import get_shop
from shuup.admin.utils.picotable import ChoicesFilter, Column, MPTTFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import Category, CategoryStatus, CategoryVisibility


class CategoryListView(PicotableListView):
    model = Category
    category_status_choices = [(status.value, status) for status in CategoryStatus if status != CategoryStatus.DELETED]
    default_columns = [
        Column("image", _("Image"), sortable=False, linked=True, raw=True),
        Column(
            "name",
            _("Name"),
            sort_field="translations__name",
            display="format_name",
            linked=True,
            allow_highlight=False,
            filter_config=MPTTFilter(choices="get_name_filter_choices", filter_field="id"),
        ),
        Column(
            "status",
            _("Status"),
            filter_config=ChoicesFilter(choices=category_status_choices, default=CategoryStatus.VISIBLE.value),
        ),
        Column(
            "visibility",
            _("Visibility"),
            filter_config=ChoicesFilter(choices=CategoryVisibility.choices),
        ),
    ]
    toolbar_buttons_provider_key = "category_list_toolbar_provider"
    mass_actions_provider_key = "category_list_mass_actions_provider"

    def get_name_filter_choices(self):
        choices = []
        shop = self.request.shop
        for c in Category.objects.all_except_deleted(shop=shop):
            name = self.format_name(c)
            choices.append((c.pk, name))
        return choices

    def get_queryset(self):
        return Category.objects.all_except_deleted(shop=get_shop(self.request))

    def format_name(self, instance, *args, **kwargs):
        level = getattr(instance, instance._mptt_meta.level_attr)
        return ("---" * level) + " " + instance.name

    def get_object_abstract(self, instance, item):
        return [
            {"text": f"{instance.name}", "class": "header"},
            {"title": _("Status"), "text": item.get("status")},
        ]
