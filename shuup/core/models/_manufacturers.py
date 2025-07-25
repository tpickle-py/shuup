from django.db import models
from django.utils.translation import gettext_lazy as _
from filer.fields.image import FilerImageField

from shuup.core.fields import InternalIdentifierField
from shuup.utils.analog import define_log_model

__all__ = ("Manufacturer",)


class Manufacturer(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("added"))
    identifier = InternalIdentifierField(unique=True)

    shops = models.ManyToManyField("shuup.Shop", blank=True, verbose_name=_("shops"))
    name = models.CharField(
        max_length=128,
        verbose_name=_("name"),
        help_text=_(
            "Enter the manufacturer’s name. "
            "Products can be filtered by the manufacturer and this can be useful for inventory and stock management."
        ),
    )
    url = models.CharField(
        null=True,
        blank=True,
        max_length=128,
        verbose_name=_("URL"),
        help_text=_(
            "Enter the URL of the product manufacturer if you would like "
            "customers to be able to visit the manufacturer's website."
        ),
    )

    logo = FilerImageField(
        verbose_name=_("logo"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="manufacturer_logos",
    )

    class Meta:
        verbose_name = _("manufacturer")
        verbose_name_plural = _("manufacturers")

    def __str__(self):  # pragma: no cover
        return f"{self.name}"


ManufacturerLogEntry = define_log_model(Manufacturer)
