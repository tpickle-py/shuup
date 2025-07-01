from django.conf import settings

from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.modules.suppliers.forms import SupplierBaseForm, SupplierContactAddressForm


class SupplierBaseFormPart(FormPart):
    priority = 1

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            SupplierBaseForm,
            template_name="shuup/admin/suppliers/_edit_base_form.jinja",
            required=True,
            kwargs={
                "instance": self.object,
                "request": self.request,
                "languages": settings.LANGUAGES,
            },
        )

    def form_valid(self, form):
        self.object = form["base"].save()


class SupplierContactAddressFormPart(FormPart):
    priority = 2

    def get_form_defs(self):
        initial = {}
        yield TemplatedFormDef(
            "address",
            SupplierContactAddressForm,
            template_name="shuup/admin/suppliers/_edit_contact_address_form.jinja",
            required=False,
            kwargs={"instance": self.object.contact_address, "initial": initial},
        )

    def form_valid(self, form):
        addr_form = form["address"]
        if addr_form.changed_data:
            addr = addr_form.save()
            self.object.contact_address = addr
            self.object.save()
