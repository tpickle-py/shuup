from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.front.utils.translation import get_shop_available_languages, set_shop_available_languages


class TranslationSettingsForm(forms.Form):
    available_languages = forms.MultipleChoiceField(
        choices=settings.LANGUAGES,
        required=False,
        label=_("Available languages in storefront"),
        help_text=_(
            "Select all the languages that should be available in storefront. "
            "Blank means that all languages should be available."
        ),
    )


class TranslationSettingsFormPart(FormPart):
    priority = 9
    name = "translation_config"
    form = TranslationSettingsForm

    def get_form_defs(self):
        if not self.object.pk:
            return
        yield TemplatedFormDef(
            name=self.name,
            form_class=self.form,
            template_name="shuup/front/admin/translation.jinja",
            required=False,
            kwargs={"initial": {"available_languages": get_shop_available_languages(self.object)}},
        )

    def form_valid(self, form):
        if self.name not in form.forms:
            return
        data = form.forms[self.name].cleaned_data
        set_shop_available_languages(self.object, data.get("available_languages", []))
