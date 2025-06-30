
from django.db import models
from django.utils.translation import ugettext_lazy as _

from shuup.core.fields import QuantityField


class ProductPackageLink(models.Model):
    parent = models.ForeignKey(
        "Product",
        related_name="linked_packages_parent",
        on_delete=models.CASCADE,
        verbose_name=_("parent product"),
    )
    child = models.ForeignKey(
        "Product",
        related_name="linked_packages_child",
        on_delete=models.CASCADE,
        verbose_name=_("child product"),
    )
    quantity = QuantityField(default=1, verbose_name=_("quantity"))

    class Meta:
        unique_together = (
            (
                "parent",
                "child",
            ),
        )
