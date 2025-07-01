from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


class HappyHour(models.Model):
    shop = models.ForeignKey("shuup.Shop", verbose_name=_("shop"), on_delete=models.CASCADE)
    name = models.CharField(
        max_length=120,
        verbose_name=_("name"),
        help_text=_("The name for this HappyHour. Used internally with exception lists for filtering."),
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("happy hour")
        verbose_name_plural = _("happy hours")


class TimeRange(models.Model):
    happy_hour = models.ForeignKey(
        on_delete=models.CASCADE,
        to="discounts.HappyHour",
        related_name="time_ranges",
        verbose_name=_("happy hour"),
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name=_("parent"),
    )
    from_hour = models.TimeField(verbose_name=_("from hour"), db_index=True)
    to_hour = models.TimeField(verbose_name=_("to hour"), db_index=True)
    weekday = models.IntegerField(verbose_name=_("weekday"), db_index=True)

    def __str__(self):
        return f"{self.weekday}-{self.pk} for {self.happy_hour}"

    class Meta:
        verbose_name = _("time range")
        verbose_name_plural = _("time ranges")
        ordering = ["weekday", "from_hour"]

    def save(self, **kwargs):
        if self.to_hour < self.from_hour:
            raise ValidationError(
                _("The value of the field `to hour` has to be later than that of `from hour`."),
                code="time_range_error",
            )

        return super().save(**kwargs)
