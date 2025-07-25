from typing import Any, Sequence, Tuple

from shuup.admin.views.select import BaseAdminObjectSelector
from shuup.core.models import Supplier


class SupplierAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 17
    model = Supplier

    def get_objects(self, search_term, *args, **kwargs) -> Sequence[Tuple[int, Any]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        search_mode = kwargs.get("searchMode")

        qs = Supplier.objects.filter(deleted=False, name__icontains=search_term)
        qs = qs.filter(shops=self.shop)
        if search_mode == "enabled":
            qs = qs.enabled(shop=self.shop)  # type: ignore
        qs = qs.values_list("id", "name")[: self.search_limit]
        return [{"id": id, "name": name} for id, name in list(qs)]  # type: ignore
