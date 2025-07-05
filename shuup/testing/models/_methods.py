from shuup.core.models import CustomCarrier, CustomPaymentProcessor, PaymentStatus


class CarrierWithCheckoutPhase(CustomCarrier):
    class Meta:
        app_label = "shuup_testing"


class PaymentWithCheckoutPhase(CustomPaymentProcessor):
    class Meta:
        app_label = "shuup_testing"

    def process_payment_return_request(self, service, order, request):
        if order.payment_status == PaymentStatus.NOT_PAID and order.payment_data.get("input_value"):
            order.payment_status = PaymentStatus.DEFERRED
            order.add_log_entry("Info! Customer promised to pay his bills.")
            order.save(update_fields=("payment_status",))
