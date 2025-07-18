from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumIntegerField

__all__ = ("Counter",)


class CounterType(Enum):
    ORDER_REFERENCE = 1

    class Labels:
        ORDER_REFERENCE = _("order reference")


class Counter(models.Model):
    id = EnumIntegerField(CounterType, primary_key=True, verbose_name=_("identifier"))
    value = models.IntegerField(default=0, verbose_name=_("value"))

    class Meta:
        verbose_name = _("counter")
        verbose_name_plural = _("counters")

    @classmethod
    def get_and_increment(cls, id):
        with transaction.atomic():
            counter, created = cls.objects.select_for_update().get_or_create(id=id)
            current = counter.value
            counter.value += 1
            counter.save()
        return current
