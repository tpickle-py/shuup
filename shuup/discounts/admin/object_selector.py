from typing import Iterable, Tuple

from shuup.admin.views.select import BaseAdminObjectSelector
from shuup.discounts.models import Discount


class DiscountAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 8
    model = Discount

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """

        qs = Discount.objects.exclude(active=False).filter(name__icontains=search_term)
        qs = qs.filter(shop=self.shop)
        if self.supplier:
            qs = qs.filter(supplier=self.supplier)
        qs = qs.values_list("id", "name")[: self.search_limit]
        return [{"id": id, "name": name} for id, name in list(qs)]
