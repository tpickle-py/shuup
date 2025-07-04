from typing import Dict, Tuple

from django import forms
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ugettext

from shuup.core.models import Contact, Shop
from shuup.front.providers import FormDefinition, FormDefProvider, FormFieldDefinition, FormFieldProvider
from shuup.gdpr.forms import CompanyAgreementForm
from shuup.utils.django_compat import is_authenticated, reverse
from shuup.utils.djangoenv import has_installed

UserModel = get_user_model()


class TextOnlyWidget(forms.Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe(self.attrs.get("value", ""))


class GDPRFormDefProvider(FormDefProvider):
    def get_definitions(self, **kwargs):
        from shuup.gdpr.models import GDPRSettings

        if not GDPRSettings.get_for_shop(self.request.shop).enabled:
            return []
        return [FormDefinition("agreement", CompanyAgreementForm, required=True)]


def get_gdpr_settings(request):
    from shuup.gdpr.models import GDPRSettings

    if not has_installed("shuup.gdpr") or not request:
        return None

    gdpr_settings = GDPRSettings.get_for_shop(request.shop)
    return gdpr_settings if gdpr_settings.enabled else None


class GDPRFieldProvider(FormFieldProvider):
    error_message = ""

    def get_fields(self, **kwargs):
        from shuup.gdpr.models import GDPRUserConsent
        from shuup.gdpr.utils import get_active_consent_pages

        request = kwargs.get("request", None)
        gdpr_settings = get_gdpr_settings(request)
        if not gdpr_settings:
            return []

        user_consent = None
        if is_authenticated(request.user):
            user_consent = GDPRUserConsent.get_for_user(request.user, request.shop)

        fields = []
        for page in get_active_consent_pages(request.shop):
            # user already has consented to this page, ignore it
            if user_consent and not user_consent.should_reconsent_to_page(page):
                continue

            key = f"accept_{page.id}"
            field = forms.BooleanField(
                label=mark_safe(
                    ugettext(
                        "I have read and accept the <a href='{}' target='_blank' class='gdpr_consent_doc_check'>{}</a>"
                    ).format(reverse("shuup:cms_page", kwargs={"url": page.url}), page.title)
                ),
                required=True,
                error_messages={"required": self.error_message},
            )
            definition = FormFieldDefinition(name=key, field=field)
            fields.append(definition)
        return fields


class GDPRRegistrationFieldProvider(GDPRFieldProvider):
    error_message = _("You must accept this in order to register.")


class GDPRCheckoutFieldProvider(GDPRFieldProvider):
    error_message = _("You must accept this to order.")


class GDPRAuthFieldProvider(GDPRFieldProvider):
    error_message = _("You must accept this in order to authenticate.")

    def get_fields(self, **kwargs):
        request = kwargs.get("request", None)
        gdpr_settings = get_gdpr_settings(request)
        if not gdpr_settings:
            return []

        if gdpr_settings.skip_consent_on_auth:
            auth_consent_text = gdpr_settings.safe_translation_getter("auth_consent_text")
            return [
                FormFieldDefinition(
                    name="auth_consent_text",
                    field=forms.CharField(
                        label="",
                        initial="",
                        required=False,
                        widget=TextOnlyWidget(attrs={"value": auth_consent_text}),
                    ),
                )
            ]
        else:
            return super().get_fields(**kwargs)


class GDPRBaseUserDataProvider:
    @classmethod
    def get_user_data(cls, shop: Shop, user: UserModel = None, contact: Contact = None) -> Tuple[str, Dict]:
        """
        Returns a tuple of string, dictionary. The string is the key that identifies the
        data and the dict contains all the user data this provider returns.
        """
        raise NotImplementedError
