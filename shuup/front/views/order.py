from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from shuup.core.models import Order
from shuup.front.signals import order_complete_viewed


class OrderCompleteView(DetailView):
    template_name = "shuup/front/order/complete.jinja"
    model = Order
    context_object_name = "order"

    def render_to_response(self, context, **response_kwargs):
        order_complete_viewed.send(sender=self, order=self.object, request=self.request)
        return super().render_to_response(context, **response_kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs["pk"], key=self.kwargs["key"])


class OrderRequiresVerificationView(DetailView):
    template_name = "shuup/front/order/requires_verification.jinja"
    model = Order

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs["pk"], key=self.kwargs["key"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.user and self.object.user.password == "//IMPLICIT//":
            from shuup.shop.views.activation_views import OneShotActivationForm

            context["activation_form"] = OneShotActivationForm()
        return context

    def get(self, request, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
