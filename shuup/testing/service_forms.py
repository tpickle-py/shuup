from shuup.admin.forms import ShuupAdminForm

from .models import CarrierWithCheckoutPhase, PaymentWithCheckoutPhase, PseudoPaymentProcessor


class PseudoPaymentProcessorForm(ShuupAdminForm):
    class Meta:
        model = PseudoPaymentProcessor
        exclude = ["identifier"]


class PaymentWithCheckoutPhaseForm(ShuupAdminForm):
    class Meta:
        model = PaymentWithCheckoutPhase
        exclude = ["identifier"]


class CarrierWithCheckoutPhaseForm(ShuupAdminForm):
    class Meta:
        model = CarrierWithCheckoutPhase
        exclude = ["identifier"]
