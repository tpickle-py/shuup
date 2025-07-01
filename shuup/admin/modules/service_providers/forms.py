from shuup.admin.forms import ShuupAdminForm
from shuup.core.models import CustomCarrier, CustomPaymentProcessor


class CustomCarrierForm(ShuupAdminForm):
    class Meta:
        model = CustomCarrier
        exclude = ("identifier",)


class CustomPaymentProcessorForm(ShuupAdminForm):
    class Meta:
        model = CustomPaymentProcessor
        exclude = ("identifier",)
