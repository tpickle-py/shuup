from django import forms
from django.utils.translation import gettext_lazy as _

from shuup.core.models import MediaFolder


class MediaFolderForm(forms.ModelForm):
    class Meta:
        model = MediaFolder
        fields = ("visible", "owners")
        labels = {"visible": _("Visible for all everyone in the media browser")}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["owners"].required = False
