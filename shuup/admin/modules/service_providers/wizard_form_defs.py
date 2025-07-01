from django.conf import settings

from shuup import configuration
from shuup.admin.views.wizard import TemplatedWizardFormDef

from .wizard_forms import ManualPaymentWizardForm, ManualShippingWizardForm


class ServiceWizardFormDef(TemplatedWizardFormDef):
    priority = 0

    def __init__(self, name, form_class, template_name, request, extra_js=""):
        shop = request.shop
        form_def_kwargs = {
            "name": name,
            "kwargs": {
                "instance": form_class._meta.model.objects.first(),
                "languages": configuration.get(shop, "languages", settings.LANGUAGES),
            },
        }
        super().__init__(
            form_class=form_class,
            template_name=template_name,
            extra_js=extra_js,
            **form_def_kwargs,
        )

    def visible(self):
        return True


class ManualShippingWizardFormDef(ServiceWizardFormDef):
    priority = 1000

    def __init__(self, request):
        super().__init__(
            name="manual_shipping",
            form_class=ManualShippingWizardForm,
            template_name="shuup/admin/service_providers/_wizard_manual_shipping_form.jinja",
            request=request,
        )


class ManualPaymentWizardFormDef(ServiceWizardFormDef):
    priority = 1000

    def __init__(self, request):
        super().__init__(
            name="manual_payment",
            form_class=ManualPaymentWizardForm,
            template_name="shuup/admin/service_providers/_wizard_manual_payment_form.jinja",
            request=request,
        )
