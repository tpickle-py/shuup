from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from registration.forms import RegistrationForm

from shuup.apps.provides import get_provide_objects
from shuup.core.models import CompanyContact, PersonContact, get_person_contact
from shuup.front.signals import company_registration_save, person_registration_save
from shuup.front.utils.companies import TaxNumberCleanMixin, company_registration_requires_approval
from shuup.utils.form_group import FormGroup
from shuup.utils.importing import cached_load


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = get_user_model()

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )

        if password2:
            validate_password(password2, self.instance)

        return password2


class CompanyForm(TaxNumberCleanMixin, forms.ModelForm):
    class Meta:
        model = CompanyContact
        fields = ["name", "name_ext", "tax_number", "email", "phone", "www"]
        help_texts = {
            "name": _("Name of the company"),
            "email": None,
            "phone": None,
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["tax_number"].required = True
        address_form = cached_load("SHUUP_ADDRESS_MODEL_FORM")()

        for field in list(self.fields):
            if field not in ("name", "tax_number", "www"):
                address_formfield = address_form.fields.get(field)
                if address_formfield:
                    self.fields[field].required = address_formfield.required
                else:
                    del self.fields[field]


class ContactPersonForm(forms.ModelForm):
    class Meta:
        model = PersonContact
        fields = ["first_name", "last_name", "email", "phone"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for field_name, formfield in self.fields.items():
            if field_name in ["first_name", "last_name", "email"]:
                formfield.required = True
                formfield.help_text = None


class PersonRegistrationForm(RegistrationForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

        for provider_cls in get_provide_objects("front_registration_field_provider"):
            provider = provider_cls()
            for definition in provider.get_fields(request=self.request):
                self.fields[definition.name] = definition.field

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if password1:
            validate_password(password1, self.instance)
        return password1

    def save(self, commit=True, *args, **kwargs):
        with atomic():
            user = super().save(*args, **kwargs)
            contact = get_person_contact(user)
            contact.add_to_shop(self.request.shop)
            person_registration_save.send(sender=type(self), request=self.request, user=user, contact=contact)
        return user


class CompanyRegistrationForm(FormGroup):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)
        address_form_cls = cached_load("SHUUP_ADDRESS_MODEL_FORM")
        self.add_form_def("company", CompanyForm, kwargs={"request": self.request})
        self.add_form_def("billing", address_form_cls)
        self.add_form_def("contact_person", ContactPersonForm)
        self.add_form_def("user_account", UserCreationForm)

        for provider_cls in get_provide_objects("front_company_registration_form_provider"):
            provider = provider_cls(self, self.request)
            for definition in provider.get_definitions():
                self.add_form_def(
                    name=definition.form_name,
                    form_class=definition.form_class,
                    required=definition.required,
                    kwargs={"shop": self.request.shop, "request": self.request},
                )

    def instantiate_forms(self):
        super().instantiate_forms()
        company_form = self.forms["company"]
        billing_form = self.forms["billing"]
        for field in list(billing_form.fields):
            billing_form.fields[field].help_text = None
            if field in company_form.fields:
                del billing_form.fields[field]

    def full_clean(self):
        super().full_clean()

        # django-registration-redux expects flat cleaned_data['email'] but FormGroup provides nested structure
        contact_person_data = self.cleaned_data.get("contact_person", {})
        contact_email = contact_person_data.get("email")
        if contact_email:
            self.cleaned_data["email"] = contact_email

    def save(self, commit=True):
        with atomic():
            company = self.forms["company"].save(commit=False)
            billing_address = self.forms["billing"].save(commit=False)
            person = self.forms["contact_person"].save(commit=False)
            user = self.forms["user_account"].save(commit=False)

            company.default_billing_address = billing_address
            company.default_shipping_address = billing_address

            for field in ["name", "name_ext", "email", "phone"]:
                setattr(billing_address, field, getattr(company, field))

            person.user = user

            user.first_name = person.first_name
            user.last_name = person.last_name
            user.email = person.email

            # If company registration requires approval,
            # company and person contacts will be created as inactive
            if company_registration_requires_approval(self.request.shop):
                company.is_active = False
                person.is_active = False

            user.save()
            person.user = user
            person.save()
            person.shops.add(self.request.shop)
            billing_address.save()
            company.default_billing_address = billing_address
            company.default_shipping_address = billing_address
            company.save()
            company.add_to_shop(self.request.shop)
            company.members.add(person)

        company_registration_save.send(sender=type(self), request=self.request, user=user, company=company)
        return user
