from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatedFields

from shuup.core.fields import InternalIdentifierField
from shuup.utils.django_compat import force_text

from ._base import TranslatableShuupModel


class Label(TranslatableShuupModel):
    identifier = InternalIdentifierField(unique=True, max_length=128, editable=True)
    created_on = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_("created on"))
    modified_on = models.DateTimeField(auto_now=True, editable=False, db_index=True, verbose_name=_("modified on"))

    translations = TranslatedFields(name=models.CharField(max_length=64, verbose_name=_("name")))

    class Meta:
        verbose_name = _("label")
        verbose_name_plural = _("labels")

    def __str__(self):
        return force_text(self.safe_translation_getter("name", default=self.identifier))
