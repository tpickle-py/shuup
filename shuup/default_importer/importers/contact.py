from django.utils.translation import gettext_lazy as _

from shuup.core.models import CompanyContact, Contact, MutableAddress, PersonContact
from shuup.importer.importing import DataImporter, ImporterExampleFile, ImportMetaBase


class AddressHandlerMeta(ImportMetaBase):
    aliases = {"name_ext": ["extension", "ext"]}

    post_save_handlers = {
        "handle_row_address": [
            "city",
            "country",
            "postal code",
            "region code",
            "street",
        ],
    }

    def handle_row_address(self, fields, row_session):
        row = row_session.row
        contact = row_session.instance
        data = {}
        for field in fields:
            data[field.replace(" ", "_")] = row.get(field, "")
        data["name"] = contact.name
        data["email"] = contact.email
        data["phone"] = contact.phone
        data["name_ext"] = contact.name_ext

        if hasattr(contact, "tax_number"):
            data["tax_number"] = contact.tax_number

        address = MutableAddress.from_data(data)
        address.save()
        contact.default_shipping_address = address
        contact.default_billing_address = address
        contact.save()

    def presave_hook(self, sess):
        sess.instance.registration_shop = sess.shop

        # if name extension is given and it's empty null fail will be risen
        if sess.instance.name_ext is None:
            sess.instance.name_ext = ""


class PersonContactImporter(DataImporter):
    identifier = "contact_importer"
    name = _("Contact Importer")
    meta_base_class = AddressHandlerMeta
    model = Contact

    example_files = [
        ImporterExampleFile(
            "person_contact_sample.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    ]

    def get_related_models(self):
        return [Contact, PersonContact]

    def get_row_model(self, row):
        return PersonContact

    @classmethod
    def get_example_file_content(cls, example_file, request):
        from shuup.default_importer.samples import get_sample_file_content

        return get_sample_file_content(example_file.file_name)


class CompanyContactImporter(DataImporter):
    identifier = "company_importer"
    name = _("Company Contact Importer")

    meta_base_class = AddressHandlerMeta
    model = Contact

    example_files = [
        ImporterExampleFile(
            "company_contact_sample.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    ]

    def get_related_models(self):
        return [Contact, CompanyContact]

    def get_row_model(self, row):
        return CompanyContact

    @classmethod
    def get_example_file_content(cls, example_file, request):
        from shuup.default_importer.samples import get_sample_file_content

        return get_sample_file_content(example_file.file_name)
