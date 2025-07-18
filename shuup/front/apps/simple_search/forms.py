import re

from django import forms
from django.conf import settings
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from shuup.core.models import Product
from shuup.core.utils import context_cache
from shuup.front.utils.sorts_and_filters import ProductListFormModifier


def get_query_words(query):
    """
    Get query words

    Split the query into words and return a list of strings.

    :type query_string: str
    :return: List of strings
    :rtype: list
    """
    word_finder = re.compile(r'"([^"]+)"|(\S+)').findall
    normalize_spaces = re.compile(r"\s{2,}").sub
    words = []
    for word in word_finder(query):
        found_word = word[0] or word[1]
        words.append(normalize_spaces(" ", found_word.strip()))
    return words


def get_compiled_query(query_string, needles):
    """
    Get compiled query

    Compile query string into `Q` objects and return it
    """
    compiled_query = None
    for word in get_query_words(query_string):
        inner_query = None
        for needle in needles:
            q = Q(**{f"{needle}__icontains": word})
            inner_query = q if inner_query is None else inner_query | q
        compiled_query = inner_query if compiled_query is None else compiled_query & inner_query
    return compiled_query


def get_product_ids_for_query_str(request, query_str, limit, product_ids=None):
    if product_ids is None:
        product_ids = []
    if not query_str:
        return []

    entry_query = get_compiled_query(query_str, settings.SHUUP_SIMPLE_SEARCH_FIELDS)
    return list(
        Product.objects.searchable(shop=request.shop, customer=request.customer)
        .exclude(id__in=product_ids)
        .filter(entry_query)
        .distinct()
        .values_list("pk", flat=True)
    )[: (limit - len(product_ids))]


def get_search_product_ids(request, query, limit=settings.SHUUP_SIMPLE_SEARCH_LIMIT):
    query = query.strip().lower()
    cache_key_elements = {
        "query": query,
        "shop": request.shop.pk,
        "customer": request.customer.pk,
    }

    key, val = context_cache.get_cached_value(
        identifier="simple_search",
        item=None,
        context=request,
        cache_key_elements=cache_key_elements,
    )
    if val is not None:
        return val

    product_ids = get_product_ids_for_query_str(request, query, limit)
    for word in query.split(" ") or []:
        if word == query:
            break
        prod_count = len(product_ids)
        if prod_count >= limit:
            break
        product_ids += get_product_ids_for_query_str(request, word.strip(), limit, product_ids)

    context_cache.set_cached_value(key, product_ids[:limit])
    return product_ids


class FilterProductListByQuery(ProductListFormModifier):
    def should_use(self, configuration):
        return True

    def get_ordering(self, configuration):
        return 0

    def get_fields(self, request, category=None):
        return [("q", forms.CharField(label=_("Search"), required=False))]

    def get_filters(self, request, data):
        if not data.get("q"):
            return Q()
        return Q(pk__in=get_search_product_ids(request, data.get("q")))

    def clean_hook(self, form):
        if form.cleaned_data.get("q"):
            form.cleaned_data["q"] = form.cleaned_data["q"].strip()
