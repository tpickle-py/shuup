from typing import Iterable, Tuple

from shuup.admin.views.select import BaseAdminObjectSelector
from shuup.core.models import Attribute


class AttributeAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 1
    model = Attribute

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        qs = Attribute.objects.translated(name__icontains=search_term).values_list(
            "id", "translations__name"
        )[: self.search_limit]
        return [{"id": id, "name": name} for id, name in list(qs)]
