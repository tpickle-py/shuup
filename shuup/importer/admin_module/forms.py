from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from enumfields import EnumField

from shuup.importer.utils import get_importer_choices
from shuup.importer.utils.importer import ImportMode


class ImportSettingsForm(forms.Form):
    import_mode = EnumField(ImportMode).formfield(
        initial=ImportMode.CREATE_UPDATE, label=_("Import mode")
    )


class ImportForm(forms.Form):
    language = forms.ChoiceField(
        label=_("Importing language"),
        choices=settings.LANGUAGES,
        help_text=_("The language of the data you want to import."),
    )
    importer = forms.ChoiceField(
        label=_("Importer"),
        help_text=_("Select a importer type matching the data you want to import"),
    )
    file = forms.FileField(label=_("File"))

    def __init__(self, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(**kwargs)
        self.fields["importer"].choices = get_importer_choices(self.request.user)
