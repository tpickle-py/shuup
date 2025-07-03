from django.db import models
from django.utils.translation import gettext_lazy as _

from shuup.core.fields import QuantityField
from shuup.utils.analog import define_log_model


class SuppliedProduct(models.Model):
    supplier = models.ForeignKey("Supplier", on_delete=models.CASCADE, verbose_name=_("supplier"))
    product = models.ForeignKey("Product", on_delete=models.CASCADE, verbose_name=_("product"))
    sku = models.CharField(db_index=True, max_length=128, verbose_name=_("SKU"))
    alert_limit = models.IntegerField(default=0, verbose_name=_("alert limit"))
    physical_count = QuantityField(editable=False, verbose_name=_("physical stock count"))
    logical_count = QuantityField(editable=False, verbose_name=_("logical stock count"))

    class Meta:
        unique_together = (
            (
                "supplier",
                "product",
            ),
        )


SuppliedProductLogEntry = define_log_model(SuppliedProduct)
