from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from shuup.admin.utils.permissions import has_permission
from shuup.admin.views.wizard import TemplatedWizardFormDef, WizardPane
from shuup.apps.provides import get_provide_objects
from shuup.core.models import PaymentMethod, ShippingMethod


class ServiceProviderTypeForm(forms.Form):
    providers = forms.CharField(label=_("Provider"), required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.provider_label = kwargs.pop("label", "")
        super().__init__(*args, **kwargs)

    def clean_providers(self):
        # TODO: Handle on frontend or use forms.MultipleChoiceField
        data = self.cleaned_data.get("providers", None)
        if not data:
            self.add_error(None, _(f"Please activate at least one {self.provider_label}."))
        return data


class ServiceWizardFormPartMixin:
    service_model: Any = None  # type: ignore[assignment]
    object: Any = None  # type: ignore[assignment]
    form_def_provide_key: str = ""  # type: ignore[assignment]
    base_name: str = ""  # type: ignore[assignment]
    request: Any = None  # type: ignore[assignment]
    provider_label: Any = ""  # type: ignore[assignment]

    def visible(self):
        service_model = getattr(self, "service_model", None)
        if not service_model:
            return False
        return not self.service_model.objects.for_shop(shop=self.object).exists()

    def _get_service_provider_form_defs(self):
        form_defs = []
        for form_def in get_provide_objects(self.form_def_provide_key):
            inst = form_def(request=self.request)
            if inst.visible():
                form_defs.append(inst)
        form_defs.sort(key=lambda form_def: getattr(form_def, "priority", 0))
        return form_defs

    def get_form_defs(self):
        service_provider_form_defs = self._get_service_provider_form_defs()

        if self.request.method == "POST":
            active_providers = self.request.POST.get(self.base_name + "-providers").split(",")
            service_provider_form_defs = list(filter(lambda x: x.name in active_providers, service_provider_form_defs))
        return [
            TemplatedWizardFormDef(
                name=self.base_name,
                template_name="shuup/admin/service_providers/_wizard_service_provider_base_form.jinja",
                extra_js="shuup/admin/service_providers/_wizard_script.jinja",
                form_class=ServiceProviderTypeForm,
                kwargs={"label": self.provider_label},
            )
        ] + service_provider_form_defs

    def form_valid(self, form_group):
        providers = form_group[self.base_name].cleaned_data.get("providers").split(",")
        for provider in providers:
            provider_form = form_group.forms.get(provider, None)
            if provider_form:
                form_group[provider].request = self.request
                form_group[provider].save()


class CarrierWizardPane(ServiceWizardFormPartMixin, WizardPane):
    identifier = "carrier"
    title = _("Carrier")
    text = _("To start shipping products right away, please add shipping methods for your shop")
    icon = "shuup_admin/img/shipping.png"
    service_model = ShippingMethod
    base_name = "shipping_method_base"
    provider_label = _("shipping method")
    form_def_provide_key = "carrier_wizard_form_def"

    def valid(self):
        return has_permission(self.request.user, "shipping_method.edit")


class PaymentWizardPane(ServiceWizardFormPartMixin, WizardPane):
    identifier = "payment"
    title = _("Payment Provider")
    text = _("To start accepting payments right away, please add payment methods for your shop")
    icon = "shuup_admin/img/payment.png"
    service_model = PaymentMethod
    base_name = "payment_method_base"
    provider_label = _("payment method")
    form_def_provide_key = "payment_processor_wizard_form_def"

    def valid(self):
        return has_permission(self.request.user, "payment_method.edit")
