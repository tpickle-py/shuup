from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from shuup.core.models import Order, PaymentUrls
from shuup.utils.django_compat import reverse


def get_payment_urls(request, order):
    """
    :type request: django.http.HttpRequest
    """
    kwargs = {"pk": order.pk, "key": order.key}

    def absolute_url_for(name):
        return request.build_absolute_uri(reverse(name, kwargs=kwargs))

    return PaymentUrls(
        payment_url=absolute_url_for("shuup:order_process_payment"),
        return_url=absolute_url_for("shuup:order_process_payment_return"),
        cancel_url=absolute_url_for("shuup:order_payment_canceled"),
    )


class ProcessPaymentView(DetailView):
    model = Order
    context_object_name = "order"

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs["pk"], key=self.kwargs["key"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["payment_urls"] = get_payment_urls(self.request, self.object)
        return context

    def dispatch(self, request, *args, **kwargs):
        mode = self.kwargs["mode"]
        order = self.object = self.get_object()

        payment_method = order.payment_method if order.payment_method_id else None
        if mode == "payment":
            if order.is_canceled():
                messages.add_message(
                    request,
                    messages.INFO,
                    _("The order is canceled so you can't pay for it."),
                )
                return redirect("shuup:order_complete", pk=order.pk, key=order.key)

            if not order.is_paid():
                if payment_method:
                    return payment_method.get_payment_process_response(
                        order=order, urls=get_payment_urls(request, order)
                    )
        elif mode == "return":
            if payment_method:
                payment_method.process_payment_return_request(order=order, request=request)
        elif mode == "cancel":
            self.template_name = "shuup/front/order/payment_canceled.jinja"
            return self.render_to_response(self.get_context_data(object=order))
        else:
            raise ImproperlyConfigured(f"Error! Unknown ProcessPaymentView mode: `{mode}`.")

        return redirect("shuup:order_complete", pk=order.pk, key=order.key)
