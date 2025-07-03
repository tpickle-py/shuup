# Shared helper functions for Shuup test factories
# Moved from factories.py to avoid circular imports
import random
import uuid

import faker
import six
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import validate_email
from django_countries.data import COUNTRIES
from faker.utils.loading import find_available_locales
from filer.models import imagemodels
from six import BytesIO

from shuup.core.models import (
    AnonymousContact,
    Attribute,
    AttributeChoiceOption,
    AttributeVisibility,
    Category,
    Contact,
    Currency,
    Manufacturer,
    MutableAddress,
    Product,
    ProductMedia,
    ProductMediaKind,
    ProductType,
    SalesUnit,
    Shop,
    ShopProduct,
    ShopProductVisibility,
    ShopStatus,
    Supplier,
    SupplierModule,
    SupplierType,
)
from shuup.core.models._attributes import AttributeType
from shuup.core.pricing import get_pricing_module
from shuup.utils.filer import filer_image_from_data

from ..image_generator import generate_image
from .shop_factory import ShopFactory

ATTR_SPECS = [
    {"type": AttributeType.BOOLEAN, "identifier": "awesome", "name": "Awesome?"},
    {"type": AttributeType.INTEGER, "identifier": "bogomips", "name": "BogoMIPS"},
    {
        "type": AttributeType.DECIMAL,
        "identifier": "surface_pressure",
        "name": "Surface pressure (kPa)",
    },
    {"type": AttributeType.TIMEDELTA, "identifier": "time_to_finish", "name": "Time to finish"},
    {"type": AttributeType.UNTRANSLATED_STRING, "identifier": "author", "name": "Author"},
    {"type": AttributeType.TRANSLATED_STRING, "identifier": "genre", "name": "Genre"},
    {"type": AttributeType.DATE, "identifier": "release_date", "name": "Release Date"},
    {
        "type": AttributeType.DATETIME,
        "identifier": "important_datetime",
        "name": "Time and Date of Eschaton",
    },
    {"type": AttributeType.CHOICES, "identifier": "list_choices", "name": "Options to select"},
]

DEFAULT_IDENTIFIER = "default"
DEFAULT_NAME = "Default"
DEFAULT_CURRENCY = "EUR"

DEFAULT_ADDRESS_DATA = {
    "prefix": "Sir",
    "name": "Dog Hello",
    "suffix": ", Esq.",
    "postal_code": "K9N",
    "street": "Woof Ave.",
    "city": "Dog Fort",
    "country": "FR",
}

COUNTRY_CODES = sorted(COUNTRIES.keys())


# Order status functions moved to order_factory.py


def default_by_identifier(model):
    return model.objects.filter(identifier=DEFAULT_IDENTIFIER).first()


def get_default_attribute_set():
    for spec in ATTR_SPECS:
        if not Attribute.objects.filter(identifier=spec["identifier"]).exists():
            attr = Attribute.objects.create(**spec)
            assert attr.pk, "attribute was saved"
            assert str(attr) == spec["name"], "attribute has correct name"
    return list(Attribute.objects.filter(identifier__in={spec["identifier"] for spec in ATTR_SPECS}))


def get_default_product_type():
    product_type = default_by_identifier(ProductType)
    if not product_type:
        product_type = ProductType.objects.create(identifier=DEFAULT_IDENTIFIER, name="Default Product Type")
        assert product_type.pk, "product type was saved"
        assert product_type.identifier == "default", "product type has requested identifier"
        for attr in get_default_attribute_set():
            product_type.attributes.add(attr)
    return product_type


def get_default_manufacturer():
    manufacturer = default_by_identifier(Manufacturer)
    if not manufacturer:
        manufacturer = Manufacturer.objects.create(identifier=DEFAULT_IDENTIFIER, name="Default Manufacturer")
        assert manufacturer.pk, "manufacturer was saved"
        assert manufacturer.identifier == "default", "manufacturer has requested identifier"
    return manufacturer


# Tax functions moved to tax_factory.py


def get_currency(code, digits=2):
    currency = Currency.objects.filter(code=code).first()
    if not currency:
        currency = Currency.objects.create(code=code, decimal_places=digits)
        assert currency.pk
    return currency


def get_default_currency():
    return get_currency(DEFAULT_CURRENCY, 2)


# Service provider functions moved to service_factory.py


# Contact group functions moved to contact_factory.py


def get_default_supplier(shop=None):
    supplier = default_by_identifier(Supplier)
    if not supplier:
        supplier = Supplier.objects.create(
            name=DEFAULT_NAME,
            identifier=DEFAULT_IDENTIFIER,
            type=SupplierType.INTERNAL,
        )
        supplier_module = SupplierModule.objects.get_or_create(module_identifier="simple_supplier")[0]
        supplier.supplier_modules.add(supplier_module)
        assert str(supplier) == DEFAULT_NAME
    if not shop:
        shop = get_default_shop()
    supplier.shops.add(shop)
    return supplier


def get_supplier(module_identifier, shop=None, **kwargs):
    name = kwargs.pop("name", DEFAULT_NAME)
    supplier = Supplier.objects.create(name=name, type=SupplierType.INTERNAL, **kwargs)
    supplier_module, _created = SupplierModule.objects.get_or_create(module_identifier=module_identifier)
    supplier.supplier_modules.add(supplier_module)
    if shop:
        supplier.shops.add(shop)
    return supplier


def get_default_shop():
    shop = default_by_identifier(Shop)
    if not shop:
        shop = Shop.objects.create(
            name=DEFAULT_NAME,
            identifier=DEFAULT_IDENTIFIER,
            status=ShopStatus.ENABLED,
            public_name=DEFAULT_NAME,
            currency=get_default_currency().code,
            domain="default.shuup.com",
        )
        assert str(shop) == DEFAULT_NAME
    return shop


def get_shop(
    prices_include_tax=True,
    currency=DEFAULT_CURRENCY,
    identifier=None,
    enabled=False,
    **kwargs,
):
    key = f"shop:{currency}/taxful={prices_include_tax}"
    values = {"prices_include_tax": prices_include_tax, "currency": currency}
    if enabled:
        values["status"] = ShopStatus.ENABLED
    values.update(kwargs)
    shop = Shop.objects.get_or_create(identifier=identifier or key, defaults=values)[0]

    # make sure that the currency is available throughout the Shuup
    get_currency(code=currency)

    # Make our default product available to the new shop
    product = get_default_product()
    sp = ShopProduct.objects.get_or_create(product=product, shop=shop)[0]
    sp.suppliers.add(get_default_supplier())

    return shop


def get_random_filer_image():
    pil_image = generate_image(32, 32)
    io = six.BytesIO()
    pil_image.save(io, "JPEG", quality=45)
    jpeg_data = io.getvalue()
    name = f"{uuid.uuid4()}.jpg"
    image = imagemodels.Image(name=name)
    image.file.save(name, ContentFile(jpeg_data))
    return image


def complete_product(product):
    image = get_random_filer_image()
    media = ProductMedia.objects.create(
        product=product,
        kind=ProductMediaKind.IMAGE,
        file=image,
        enabled=True,
        public=True,
    )
    product.primary_image = media
    product.save()
    assert product.primary_image_id
    sp = ShopProduct.objects.create(
        product=product,
        shop=get_default_shop(),
        visibility=ShopProductVisibility.ALWAYS_VISIBLE,
    )
    sp.suppliers.add(get_default_supplier())


def create_product(sku, shop=None, supplier=None, default_price=None, **attrs):
    from .tax_factory import get_default_tax_class
    
    if shop is None:
        shop = ShopFactory()
    if default_price is not None:
        default_price = shop.create_price(default_price)
    if "fractional" in attrs:
        attrs.pop("fractional")
        get_sales_unit = get_fractional_sales_unit
    else:
        get_sales_unit = get_default_sales_unit
    product_attrs = {
        "type": get_default_product_type(),
        "tax_class": get_default_tax_class(),
        "sku": sku,
        "name": sku.title(),
        "width": 100,
        "height": 100,
        "depth": 100,
        "net_weight": 100,
        "gross_weight": 100,
        "sales_unit": get_sales_unit(),
    }
    product_attrs.update(attrs)
    product = Product(**product_attrs)
    product.full_clean()
    product.save()
    sp = ShopProduct.objects.create(
        product=product,
        shop=shop,
        default_price=default_price,
        visibility=ShopProductVisibility.ALWAYS_VISIBLE,
    )
    if supplier:
        sp.suppliers.add(supplier)
    sp.save()
    return product


def get_default_product():
    product = Product.objects.filter(sku=DEFAULT_IDENTIFIER).first()
    if not product:
        product = create_product(DEFAULT_IDENTIFIER)
        complete_product(product)
    return product


def get_default_shop_product():
    shop = get_default_shop()
    product = get_default_product()
    shop_product = product.get_shop_instance(shop)
    shop_product.visibility = ShopProductVisibility.ALWAYS_VISIBLE
    shop_product.save()
    return shop_product


def get_default_sales_unit():
    unit = default_by_identifier(SalesUnit)
    if not unit:
        unit = SalesUnit.objects.create(
            identifier=DEFAULT_IDENTIFIER,
            decimals=0,
            name=DEFAULT_NAME,
            symbol=DEFAULT_NAME[:3].lower(),
        )
        assert str(unit) == DEFAULT_NAME
    return unit


def get_fractional_sales_unit():
    return SalesUnit.objects.create(identifier="fractional", decimals=2, name="Fractional unit", short_name="fra")


def get_default_category():
    category = default_by_identifier(Category)
    if not category:
        category = Category.objects.create(
            parent=None,
            identifier=DEFAULT_IDENTIFIER,
            name=DEFAULT_NAME,
        )
        category.shops.add(get_default_shop())
        assert str(category) == DEFAULT_NAME
    return category


# Permission group functions moved to contact_factory.py


def get_faker(providers, locale="en"):
    providers = [(f"faker.providers.{provider}" if ("." not in provider) else provider) for provider in providers]
    locale = locale or (random.choice(["en_US"] + list(find_available_locales(providers))))
    fake = faker.Factory.create(locale=locale)
    # Remove assignments to fake.locale, fake.locale_language, fake.language (not valid attributes)
    # Instead, use fake.locales or locale directly if needed
    return fake


# User creation functions moved to contact_factory.py


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


# Order creation functions moved to order_factory.py


def create_random_product_attribute():
    type_choices = list(AttributeType)
    vis_choices = list(AttributeVisibility)

    last_id = Attribute.objects.count() + 1
    fake_product_color = get_faker(["color"]).format("color_name")
    name = f"{fake_product_color} {last_id}"  # type: ignore
    identifier = name.lower().replace(" ", "-")

    return Attribute.objects.create(
        identifier=identifier,
        type=random.choice(type_choices),
        visibility_mode=random.choice(vis_choices),
        name=name,
    )


def _get_pricing_context(shop, customer=None):
    return get_pricing_module().get_context_from_data(
        shop=shop,
        customer=(customer or AnonymousContact()),
    )


def get_all_seeing_key(user_or_contact):
    # Confirmed: Contact.user attribute exists in Django 3+
    if isinstance(user_or_contact, Contact):
        user = getattr(user_or_contact, "user", None)
    else:
        user = user_or_contact
    return f"is_all_seeing:{getattr(user, 'pk', 'unknown')}"


# Contact and order functions moved to respective factory files


def _generate_product_image(product):
    image = generate_image(32, 32)
    sio = BytesIO()
    image.save(sio, format="JPEG", quality=75)
    filer_file = filer_image_from_data(
        request=None,
        path="ProductImages/Mock",
        file_name=f"{product.sku}.jpg",
        file_data=sio.getvalue(),
        sha1=True,
    )
    media = ProductMedia.objects.create(product=product, kind=ProductMediaKind.IMAGE, file=filer_file)
    media.shops.set(Shop.objects.all())
    media.save()
    return media


def create_attribute_with_options(name, options, min_options=0, max_options=0):
    attribute = Attribute.objects.create(
        identifier=name,
        name=name,
        type=AttributeType.CHOICES,
        min_choices=min_options,
        max_choices=max_options,
    )
    for option in options:
        AttributeChoiceOption.objects.create(attribute=attribute, name=option)
    return attribute


# Order manipulation functions moved to order_factory.py


def create_package_product(sku, shop=None, supplier=None, default_price=None, children=4, **attrs):
    package_product = create_product(sku, shop, supplier, default_price, **attrs)
    assert not package_product.get_package_child_to_quantity_map()
    children_products = [create_product(f"PackageChild-{x}", shop=shop, supplier=supplier) for x in range(children)]
    package_def = {child: 1 + idx for (idx, child) in enumerate(children_products)}
    package_product.make_package(package_def)
    assert package_product.is_package_parent()
    package_product.save()
    return package_product
