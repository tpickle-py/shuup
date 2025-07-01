from typing import Iterable, Tuple

from django.contrib.auth import get_user_model
from django.db.models.query_utils import Q

from shuup.admin.views.select import BaseAdminObjectSelector

User = get_user_model()


class UserAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 20
    model = User

    def get_objects(self, search_term, *args, **kwargs) -> Iterable[Tuple[int, str]]:
        """
        Returns an iterable of tuples of (id, text)
        """

        qs = User.objects.filter(Q(username__icontains=search_term) | Q(email__icontains=search_term))
        qs = qs.values_list("pk", "username")[: self.search_limit]
        return [{"id": id, "name": name} for id, name in list(qs)]
