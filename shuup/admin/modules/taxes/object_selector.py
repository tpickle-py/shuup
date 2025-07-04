from typing import Any, Dict, List

from shuup.admin.views.select import BaseAdminObjectSelector
from shuup.core.models import CustomerTaxGroup, Tax, TaxClass


class TaxAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 18
    model = Tax

    def get_objects(self, search_term, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        qs = (
            Tax.objects.exclude(enabled=False)
            .translated(name__icontains=search_term)  # type: ignore[attr-defined]
            .values_list("id", "translations__name")[: self.search_limit]
        )
        return [{"id": id, "name": name} for id, name in list(qs)]


class CustomerTaxGroupAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 18
    model = CustomerTaxGroup

    def get_objects(self, search_term, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        qs = CustomerTaxGroup.objects.translated(name__icontains=search_term).values_list(  # type: ignore[attr-defined]
            "id", "translations__name"
        )
        qs = qs[: self.search_limit]
        return [{"id": id, "name": name} for id, name in list(qs)]


class TaxClassAdminObjectSelector(BaseAdminObjectSelector):
    ordering = 19
    model = TaxClass

    def get_objects(self, search_term, *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Returns an iterable of tuples of (id, text)
        """
        translated_qs = TaxClass.objects.translated(name__icontains=search_term)  # type: ignore[attr-defined]
        qs = translated_qs.values_list("id", "translations__name")[: self.search_limit]
        return [{"id": id, "name": name} for id, name in list(qs)]
