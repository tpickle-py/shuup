from typing import Iterable, Tuple

from django.contrib.auth.models import Group as PermissionGroup

from shuup.admin.views.select import BaseAdminObjectSelector


class PermissionGroupAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 9
    model = PermissionGroup

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        qs = PermissionGroup.objects.filter(name__icontains=search_term).values_list("id", "name")[: self.search_limit]
        return [{"id": id, "name": name} for id, name in list(qs)]
