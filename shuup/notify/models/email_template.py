from django.db import models
from django.utils.translation import gettext_lazy as _


class EmailTemplate(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=60)
    template = models.TextField(
        verbose_name=_("Template"),
        help_text=_(
            "Enter the base HTML template to be used in emails. "
            "Mark the place to inject the email content using the variable `%html_body%` inside the body."
        ),
    )

    class Meta:
        verbose_name = _("Email Template")
        verbose_name_plural = _("Email Templates")

    def __str__(self):
        return self.name
