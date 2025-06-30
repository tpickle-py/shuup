from typing import Iterable, Tuple

from shuup.admin.views.select import BaseAdminObjectSelector
from shuup.core.models import Category


class CategoryAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 2
    model = Category

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        search_mode = kwargs.get("searchMode")

        if search_mode == "visible":
            qs = Category.objects.all_visible(customer=None, shop=self.shop)
        else:
            qs = Category.objects.all_except_deleted(shop=self.shop)
        qs = qs.translated(name__icontains=search_term)
        qs = qs.values_list("id", "translations__name")[: self.search_limit]

        return [{"id": id, "name": name} for id, name in list(qs)]
