

from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from shuup_mirage_field.fields import EncryptedCharField

from ._base import ShuupModel
from ._shops import Shop


class ConfigurationItem(ShuupModel):
    shop = models.ForeignKey(
        on_delete=models.CASCADE,
        to=Shop,
        related_name="+",
        null=True,
        blank=True,
        verbose_name=_("shop"),
    )
    key = models.CharField(verbose_name=_("key"), max_length=100)
    value = JSONField(verbose_name=_("value"))

    class Meta:
        unique_together = [("shop", "key")]
        verbose_name = _("configuration item")
        verbose_name_plural = _("configuration items")

    def __str__(self):
        if self.shop:
            return _("%(key)s for shop %(shop)s") % {"key": self.key, "shop": self.shop}
        else:
            return _("%(key)s (global)") % {"key": self.key}

    def __repr__(self):
        return f'<{type(self).__name__} "{self.key}" for {self.shop!r}>'



class EncryptedConfigurationItem(ShuupModel):
    shop = models.ForeignKey(
        on_delete=models.CASCADE,
        to=Shop,
        related_name="+",
        null=True,
        blank=True,
        verbose_name=_("shop"),
    )
    key = models.CharField(verbose_name=_("key"), max_length=100)
    value = EncryptedCharField(verbose_name=_("value"))

    class Meta:
        unique_together = [("shop", "key")]
        verbose_name = _("configuration item")
        verbose_name_plural = _("configuration items")

    def __str__(self):
        if self.shop:
            return _("%(key)s for shop %(shop)s") % {"key": self.key, "shop": self.shop}
        else:
            return _("%(key)s (global)") % {"key": self.key}

    def __repr__(self):
        return f'<{type(self).__name__} "{self.key}" for {self.shop!r}>'
