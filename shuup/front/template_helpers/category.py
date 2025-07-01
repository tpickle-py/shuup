from django.utils.translation import get_language

from shuup.compat import contextfunction
from shuup.core.models import Manufacturer


@contextfunction
def get_manufacturers(context):
    request = context["request"]
    category = context["category"]
    manufacturers_ids = (
        category.products.all_visible(request, language=get_language()).values_list("manufacturer__id").distinct()
    )
    return Manufacturer.objects.filter(pk__in=manufacturers_ids)
