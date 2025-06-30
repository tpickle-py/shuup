from typing import Iterable, Tuple

from shuup.admin.views.select import BaseAdminObjectSelector
from shuup.campaigns.models.campaigns import Coupon


class CouponAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 7
    model = Coupon

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """

        qs = Coupon.objects.exclude(active=False).filter(code__icontains=search_term)
        qs = qs.filter(shop=self.shop)
        if self.supplier:
            qs = qs.filter(supplier=self.supplier)
        qs = qs.values_list("id", "code")[: self.search_limit]
        return [{"id": id, "name": name} for id, name in list(qs)]
