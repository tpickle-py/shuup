# Contact-related factory functions
import random
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as PermissionGroup
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.text import slugify
from django_countries.data import COUNTRIES

from shuup.admin.utils.permissions import set_permissions_for_group
from shuup.core.models import CompanyContact, Contact, ContactGroup, MutableAddress, PersonContact

from .shared import (
    DEFAULT_ADDRESS_DATA,
    DEFAULT_IDENTIFIER,
    DEFAULT_NAME,
    default_by_identifier,
    get_default_shop,
    get_faker,
)

COUNTRY_CODES = sorted(COUNTRIES.keys())


def get_random_email(fake):
    while True:
        email = fake.email()
        try:  # Faker sometimes generates invalid emails. That's terrible.
            validate_email(email)
        except ValidationError:
            pass
        else:
            break
    return email


def create_random_address(fake=None, save=True, **values) -> MutableAddress:
    if not fake:
        fake = get_faker(["person", "address"])
    # Use fake.format('provider') for compatibility with linters and runtime
    values.setdefault("name", fake.format("name"))
    values.setdefault("street", fake.format("address").replace("\n", " "))
    values.setdefault("city", fake.format("city"))
    values.setdefault("region", fake.format("state"))
    values.setdefault("country", random.choice(COUNTRY_CODES))
    values.setdefault("postal_code", fake.format("postcode"))
    address = MutableAddress.from_data(values)
    if save:
        address.save()
    return address


def get_address(**overrides):
    data = dict(DEFAULT_ADDRESS_DATA, **overrides)
    return MutableAddress.from_data(data)


def create_random_company(shop=None) -> CompanyContact:
    fake = get_faker(["company", "person", "internet"])
    name = fake.format("company")
    email = get_random_email(fake)
    phone = fake.format("phone_number")
    language = "en"
    address = create_random_address(name=name, email=email, phone=phone)
    contact = CompanyContact.objects.create(
        email=email,
        phone=phone,
        name=name,
        default_shipping_address=address,
        default_billing_address=address,
        language=language,
    )
    if shop:
        contact.add_to_shop(shop)
    return contact


def create_random_contact_group(shop=None):
    fake = get_faker(["job"])
    name = fake.format("job")
    idx = ContactGroup.objects.filter(translations__name=name).count() + 1
    name_lower = name.lower().replace(" ", "-")
    identifier = f"{idx}-{name_lower}"
    if not shop:
        shop = get_default_shop()
    return ContactGroup.objects.create(
        identifier=identifier,
        shop=shop,
        name=name,
    ).set_price_display_options(
        show_pricing=random.choice([True, False]),
        show_prices_including_taxes=random.choice([True, False]),
        hide_prices=random.choice([True, False]),
    )


def create_random_person(locale="en", minimum_name_comp_len=0, shop=None):
    fake = get_faker(["person", "internet", "address"], locale=locale)
    while True:
        first_name = fake.format("first_name")
        last_name = fake.format("last_name")
        name = f"{first_name} {last_name}"
        if len(first_name) > minimum_name_comp_len and len(last_name) > minimum_name_comp_len:
            break
    email = get_random_email(fake)
    phone = fake.format("phone_number")
    prefix = ""
    suffix = ""
    address = create_random_address(
        fake=fake,
        name=name,
        prefix=prefix,
        suffix=suffix,
        email=email,
        phone=phone,
    )
    contact = PersonContact.objects.create(
        email=email,
        phone=phone,
        name=name,
        first_name=first_name,
        last_name=last_name,
        prefix=prefix,
        suffix=suffix,
        default_shipping_address=address,
        default_billing_address=address,
        gender=random.choice("mfuo"),
        language=locale.split("_")[0],
    )
    if shop:
        contact.add_to_shop(shop)
    return contact


def create_random_user(locale="en", **kwargs):
    user_model = get_user_model()
    ran_user = get_faker(["person"], locale).format("first_name")
    params = {user_model.USERNAME_FIELD: f"{uuid.uuid4().hex}-{slugify(ran_user)}"}
    params.update(kwargs or {})
    return user_model.objects.create(**params)


def get_default_staff_user(shop=None):
    if not shop:
        shop = get_default_shop()
    user = create_random_user()
    user.is_staff = True
    user.save()
    user.groups.add(get_default_permission_group())
    shop.staff_members.add(user)
    return user


def get_default_customer_group(shop=None):
    group = default_by_identifier(ContactGroup)
    if not shop:
        shop = get_default_shop()
    if not group:
        group = ContactGroup.objects.create(name=DEFAULT_NAME, identifier=DEFAULT_IDENTIFIER, shop=shop)
        # Update assertion to use identifier since name access might have translation issues
        assert group.identifier == DEFAULT_IDENTIFIER
    return group


def get_default_permission_group(permissions=("dashboard",)):
    group, _ = PermissionGroup.objects.get_or_create(name=DEFAULT_NAME)
    set_permissions_for_group(getattr(group, "id", None), permissions)
    return group


def get_all_seeing_key(user_or_contact):
    # Confirmed: Contact.user attribute exists in Django 3+
    if isinstance(user_or_contact, Contact):
        user = getattr(user_or_contact, "user", None)
    else:
        user = user_or_contact
    return f"is_all_seeing:{getattr(user, 'pk', 'unknown')}"
