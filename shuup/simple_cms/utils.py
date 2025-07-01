from django.db.models import Case, When


def order_query_by_values(queryset, values):
    order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(values)])
    if values:
        queryset = queryset.order_by(order)
    return queryset
