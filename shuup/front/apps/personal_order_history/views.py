import django.views.generic
from django.http import HttpResponseRedirect
from django.views.generic import View

from shuup.core.models import Order, ProductMode
from shuup.front.views.dashboard import DashboardViewMixin
from shuup.utils.django_compat import reverse


class OrderViewMixin:
    model = Order

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(customer=self.request.customer)


class OrderListView(DashboardViewMixin, OrderViewMixin, django.views.generic.ListView):
    template_name = "shuup/personal_order_history/order_list.jinja"
    context_object_name = "orders"


class OrderDetailView(DashboardViewMixin, OrderViewMixin, django.views.generic.DetailView):
    template_name = "shuup/personal_order_history/order_detail.jinja"
    context_object_name = "order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reorderable_lines = _get_reorderable_lines(context["order"])
        context["order_is_reorderable"] = reorderable_lines.exists()
        return context


class ReorderView(View):
    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(customer=request.customer, pk=kwargs["pk"])
        except Order.DoesNotExist:
            return HttpResponseRedirect(reverse("shuup:show-order", kwargs=kwargs))

        for line in _get_reorderable_lines(order):
            request.basket.add_product(
                supplier=line.supplier,
                shop=request.shop,
                product=line.product,
                quantity=line.quantity,
            )

        return HttpResponseRedirect(reverse("shuup:basket"))


def _get_reorderable_lines(order):
    """
    Get re-orderable lines of an order.

    This is all product lines except:
     * child lines, because otherwise package contents are added twice.
     * subscriptions, because those don't use normal checkout flow.
    """
    return order.lines.products().exclude(parent_line__isnull=False).exclude(product__mode=ProductMode.SUBSCRIPTION)
