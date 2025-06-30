from django.views.generic import DeleteView

from shuup.core.models import PaymentMethod, ShippingMethod
from shuup.utils.django_compat import reverse_lazy


class PaymentMethodDeleteView(DeleteView):
    model = PaymentMethod
    success_url = reverse_lazy("shuup_admin:payment_method.list")


class ShippingMethodDeleteView(DeleteView):
    model = ShippingMethod
    success_url = reverse_lazy("shuup_admin:shipping_method.list")
