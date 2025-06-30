


from django.conf import settings

from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.modules.services.forms import PaymentMethodForm, ShippingMethodForm


class ServiceBaseFormPart(FormPart):
    priority = -1000  # Show this first
    form = None  # Override in subclass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            self.form,
            required=True,
            template_name="shuup/admin/services/_edit_base_form.jinja",
            kwargs={
                "instance": self.object,
                "languages": settings.LANGUAGES,
                "request": self.request,
            },
        )

    def form_valid(self, form):
        self.object = form["base"].save()
        return self.object


class ShippingMethodBaseFormPart(ServiceBaseFormPart):
    form = ShippingMethodForm


class PaymentMethodBaseFormPart(ServiceBaseFormPart):
    form = PaymentMethodForm
