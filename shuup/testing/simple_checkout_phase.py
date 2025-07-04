from django import forms
from django.views.generic.edit import FormView

from shuup.front.checkout import BasicServiceCheckoutPhaseProvider, CheckoutPhaseViewMixin

from .models import CarrierWithCheckoutPhase, PaymentWithCheckoutPhase


class TestPaymentCheckoutPhaseForm(forms.Form):
    input_field = forms.BooleanField(required=True, label="I promise to pay this order")


class TestShipmentCheckoutPhaseForm(forms.Form):
    input_field = forms.CharField(required=True, label="Enter your postal code")


class TestMethodCheckoutPhase(CheckoutPhaseViewMixin, FormView):
    template_name = "shuup_testing/simple_checkout_phase.jinja"
    data_attribute = None  # Override in subclass
    storage_identifier = None  # Override in subclass

    def get_initial(self):
        initial = super().get_initial()
        storage = self.storage.get(self.storage_identifier)
        if storage:
            initial.update({"input_field": storage.get("input_value")})
        return initial

    def form_valid(self, form):
        self.storage[self.storage_identifier] = {
            "input_value": form.cleaned_data.get("input_field"),
        }
        return super().form_valid(form)

    def is_valid(self):
        data = self.storage.get(self.storage_identifier, {})
        return bool(data.get("input_value"))

    def process(self):
        data = self.storage.get(self.storage_identifier, {})
        basket_data = getattr(self.request.basket, self.data_attribute)
        basket_data["input_value"] = data.get("input_value")


class TestPaymentCheckoutPhase(TestMethodCheckoutPhase):
    identifier = "test_payment_phase"
    title = "Test Payment Phase"
    form_class = TestPaymentCheckoutPhaseForm
    storage_identifier = "payment_with_checkout_phase"
    data_attribute = "payment_data"


class TestShipmentCheckoutPhase(TestMethodCheckoutPhase):
    identifier = "test_shipment_phase"
    title = "Test Shipment Phase"
    form_class = TestShipmentCheckoutPhaseForm
    storage_identifier = "shipment_with_checkout_phase"
    data_attribute = "shipping_data"


class PaymentPhaseProvider(BasicServiceCheckoutPhaseProvider):
    phase_class = TestPaymentCheckoutPhase
    service_provider_class = PaymentWithCheckoutPhase


class ShipmentPhaseProvider(BasicServiceCheckoutPhaseProvider):
    phase_class = TestShipmentCheckoutPhase
    service_provider_class = CarrierWithCheckoutPhase
