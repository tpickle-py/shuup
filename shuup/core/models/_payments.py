from django.db import models
from django.utils.translation import gettext_lazy as _

from shuup.core.fields import CurrencyField, MoneyValueField
from shuup.utils.analog import define_log_model
from shuup.utils.properties import MoneyProperty, MoneyPropped

__all__ = ("Payment",)


# TODO (2.0): Rename this to Payment
class AbstractPayment(MoneyPropped, models.Model):
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("created on"))
    gateway_id = models.CharField(max_length=32, verbose_name=_("gateway ID"))  # TODO: do we need this?
    payment_identifier = models.CharField(max_length=96, unique=True, verbose_name=_("identifier"))

    amount = MoneyProperty("amount_value", "currency")
    foreign_amount = MoneyProperty("foreign_amount_value", "foreign_currency")

    amount_value = MoneyValueField(verbose_name=_("amount"))
    foreign_amount_value = MoneyValueField(default=None, blank=True, null=True, verbose_name=_("foreign amount"))
    foreign_currency = CurrencyField(default=None, blank=True, null=True, verbose_name=_("foreign amount currency"))

    description = models.CharField(max_length=256, blank=True, verbose_name=_("description"))

    class Meta:
        abstract = True


# TODO (2.0): Rename this to OrderPayment
class Payment(AbstractPayment):
    order = models.ForeignKey(
        "Order",
        related_name="payments",
        on_delete=models.PROTECT,
        verbose_name=_("order"),
    )

    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")

    @property
    def currency(self):
        return self.order.currency


PaymentLogEntry = define_log_model(Payment)
