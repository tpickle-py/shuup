from django import forms
from django.utils.translation import gettext_lazy as _


class PrintoutsEmailForm(forms.Form):
    to = forms.EmailField(max_length=256, label=_("To"))
    subject = forms.CharField(max_length=256, label=_("Email Subject"))
    body = forms.CharField(max_length=512, widget=forms.Textarea, label=_("Email Body"))
