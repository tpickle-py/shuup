from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from shuup import configuration
from shuup.core.utils import tax_numbers


def allow_company_registration(shop):
    return configuration.get(shop, "allow_company_registration", default=False)


def company_registration_requires_approval(shop):
    return configuration.get(shop, "company_registration_requires_approval", default=False)


def validate_tax_number(shop):
    return configuration.get(shop, "validate_tax_number", default=False)


class TaxNumberCleanMixin:
    company_name_field = "name"

    def clean_tax_number(self):
        tax_number = self.cleaned_data["tax_number"].strip()
        if self.request and validate_tax_number(self.request.shop) and tax_number:
            if tax_numbers.validate(tax_number) != "vat":
                raise ValidationError(_("Tax number is not valid."), code="not_valid_tax_number")

        return tax_number
