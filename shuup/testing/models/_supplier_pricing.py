from django.db import models

from shuup.core.fields import MoneyValueField
from shuup.utils.properties import MoneyPropped, PriceProperty


class SupplierPrice(MoneyPropped, models.Model):
    shop = models.ForeignKey(on_delete=models.CASCADE, to="shuup.Shop")
    supplier = models.ForeignKey(on_delete=models.CASCADE, to="shuup.Supplier")
    product = models.ForeignKey(on_delete=models.CASCADE, to="shuup.Product")
    amount_value = MoneyValueField()
    amount = PriceProperty("amount_value", "shop.currency", "shop.prices_include_tax")

    class Meta:
        app_label = "shuup.testing"
