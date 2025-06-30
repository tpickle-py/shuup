from typing import Iterable, Tuple

from shuup.admin.views.select import BaseAdminObjectSelector
from shuup.core.models import Manufacturer


class ManufacturerAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 6
    model = Manufacturer

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        qs = Manufacturer.objects.filter(name__icontains=search_term).values_list(
            "id", "name"
        )[: self.search_limit]
        return [{"id": id, "name": name} for id, name in list(qs)]
