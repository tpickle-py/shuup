from django.db import models
from django.utils.translation import gettext_lazy as _
from jsonfield import JSONField


class PersistentCacheEntry(models.Model):
    module = models.CharField(max_length=64, verbose_name=_("module"))
    key = models.CharField(max_length=64, verbose_name=_("key"))
    time = models.DateTimeField(auto_now=True, verbose_name=_("time"))
    data = JSONField(verbose_name=_("data"))

    class Meta:
        verbose_name = _("cache entry")
        verbose_name_plural = _("cache entries")
        unique_together = (("module", "key"),)
