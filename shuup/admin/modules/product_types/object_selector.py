from typing import Iterable, Tuple

from shuup.admin.views.select import BaseAdminObjectSelector
from shuup.core.models import ProductType


class ProductTypeAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 10
    model = ProductType

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        qs = ProductType.objects.translated(name__icontains=search_term).values_list(
            "id", "translations__name"
        )[: self.search_limit]
        return [{"id": id, "name": name} for id, name in list(qs)]
