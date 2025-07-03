# Shared helper functions for Shuup test factories
# Moved from factories.py to avoid circular imports
import datetime
import random
import uuid
from decimal import Decimal

import faker
import six
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as PermissionGroup
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import validate_email
from django.db.transaction import atomic
from django.utils.text import slugify
from django.utils.timezone import now
from django_countries.data import COUNTRIES
from faker.utils.loading import find_available_locales
from filer.models import imagemodels
from six import BytesIO

from shuup.admin.utils.permissions import set_permissions_for_group
from shuup.core.defaults.order_statuses import create_default_order_statuses
from shuup.core.models import (
    AnonymousContact,
    Attribute,
    AttributeChoiceOption,
    AttributeVisibility,
    Basket,
    Category,
    CompanyContact,
    Contact,
    ContactGroup,
    Currency,
    CustomCarrier,
    CustomPaymentProcessor,
    FixedCostBehaviorComponent,
    Manufacturer,
    MutableAddress,
    Order,
    OrderLine,
    OrderLineTax,
    OrderLineType,
    OrderStatus,
    PaymentMethod,
    PersonContact,
    Product,
    ProductMedia,
    ProductMediaKind,
    ProductType,
    SalesUnit,
    ShippingMethod,
    Shop,
    ShopProduct,
    ShopProductVisibility,
    ShopStatus,
    Supplier,
    SupplierModule,
    SupplierType,
    Tax,
    TaxClass,
    WaivingCostBehaviorComponent,
)
from shuup.core.models._attributes import AttributeType
from shuup.core.order_creator import OrderCreator, OrderSource
from shuup.core.pricing import get_pricing_module
from shuup.core.shortcuts import update_order_line_from_product
from shuup.core.taxing.utils import stacked_value_added_taxes
from shuup.default_tax.models import TaxRule
from shuup.utils.filer import filer_image_from_data
from shuup.utils.money import Money

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


def get_initial_order_status():
    create_default_order_statuses()
    # Confirmed: get_default_initial exists and works in Django 3+
    return OrderStatus.objects.get_default_initial()


def get_completed_order_status():
    create_default_order_statuses()
    # Confirmed: get_default_complete exists and works in Django 3+
    return OrderStatus.objects.get_default_complete()


# Shared helper functions moved from factories.py
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


def get_tax(code, name, rate=None, amount=None):
    assert amount is None or isinstance(amount, Money)
    tax = Tax.objects.filter(code=code).first()
    if not tax:
        tax = Tax.objects.create(
            code=code,
            name=name,
            rate=Decimal(rate) if rate is not None else None,
            amount_value=getattr(amount, "value", None),
            currency=getattr(amount, "currency", None),
        )
        assert tax.pk
        assert name in str(tax)
    return tax


def create_default_tax_rule(tax):
    tr = TaxRule.objects.filter(tax=tax).first()
    if not tr:
        tr = TaxRule.objects.create(tax=tax)
        tr.tax_classes.add(get_default_tax_class())
    return tr


def get_default_tax():
    tax = get_tax(DEFAULT_IDENTIFIER, DEFAULT_NAME, Decimal("0.5"))
    create_default_tax_rule(tax)  # Side-effect, but useful
    return tax


def get_test_tax(rate):
    name = f"TEST_{rate}"
    return get_tax(name, name, rate)


def get_default_tax_class():
    tax_class = default_by_identifier(TaxClass)
    if not tax_class:
        tax_class = TaxClass.objects.create(
            identifier=DEFAULT_IDENTIFIER,
            name=DEFAULT_NAME,
            # tax_rate=Decimal("0.5"),
        )
        assert tax_class.pk
        assert str(tax_class) == DEFAULT_NAME
    return tax_class


def get_currency(code, digits=2):
    currency = Currency.objects.filter(code=code).first()
    if not currency:
        currency = Currency.objects.create(code=code, decimal_places=digits)
        assert currency.pk
    return currency


def get_default_currency():
    return get_currency(DEFAULT_CURRENCY, 2)


def get_custom_payment_processor():
    return _get_service_provider(CustomPaymentProcessor)


def get_payment_processor_with_checkout_phase():
    raise NotImplementedError("get_payment_processor_with_checkout_phase requires PaymentWithCheckoutPhase model.")


def get_custom_carrier():
    return _get_service_provider(CustomCarrier)


def _get_service_provider(model):
    identifier = model.__name__
    service_provider = model.objects.filter(identifier=identifier).first()
    if not service_provider:
        service_provider = model.objects.create(
            identifier=identifier,
            name=model.__name__,
        )
        assert service_provider.pk and service_provider.identifier == identifier
    return service_provider


def get_default_payment_method():
    return get_payment_method()


def get_payment_method(shop=None, price=None, waive_at=None, name=None):
    return _get_service(
        PaymentMethod,
        CustomPaymentProcessor,
        name=name,
        shop=shop,
        price=price,
        waive_at=waive_at,
    )


def get_default_shipping_method():
    return get_shipping_method()


def get_shipping_method(shop=None, price=None, waive_at=None, name=None):
    return _get_service(
        ShippingMethod,
        CustomCarrier,
        name=name,
        shop=shop,
        price=price,
        waive_at=waive_at,
    )


def _get_service(service_model, provider_model, name, shop=None, price=None, waive_at=None):
    default_shop = get_default_shop()
    if shop is None:
        shop = default_shop
    if shop == default_shop and not price and not waive_at and not name:
        identifier = DEFAULT_IDENTIFIER
    else:
        identifier = f"{name}-{shop.pk}-{repr(price)}-{repr(waive_at)}"
    service = service_model.objects.filter(identifier=identifier).first()
    if not service:
        provider = _get_service_provider(provider_model)
        service = provider.create_service(
            None,
            identifier=identifier,
            shop=shop,
            enabled=True,
            name=(name or service_model.__name__),
            tax_class=get_default_tax_class(),
        )
        if price and waive_at is None:
            service.behavior_components.add(FixedCostBehaviorComponent.objects.create(price_value=price))
        elif price:
            service.behavior_components.add(
                WaivingCostBehaviorComponent.objects.create(price_value=price, waive_limit_value=waive_at)
            )
    assert service.pk and service.identifier == identifier
    assert service.shop == shop
    return service


def get_default_customer_group(shop=None):
    group = default_by_identifier(ContactGroup)
    if not shop:
        shop = get_default_shop()
    if not group:
        group = ContactGroup.objects.create(name=DEFAULT_NAME, identifier=DEFAULT_IDENTIFIER, shop=shop)
        assert str(group) == DEFAULT_NAME
    return group


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


def get_default_permission_group(permissions=("dashboard",)):
    group, _ = PermissionGroup.objects.get_or_create(name=DEFAULT_NAME)
    set_permissions_for_group(getattr(group, "id", None), permissions)
    return group


def get_faker(providers, locale="en"):
    providers = [(f"faker.providers.{provider}" if ("." not in provider) else provider) for provider in providers]
    locale = locale or (random.choice(["en_US"] + list(find_available_locales(providers))))
    fake = faker.Factory.create(locale=locale)
    # Remove assignments to fake.locale, fake.locale_language, fake.language (not valid attributes)
    # Instead, use fake.locales or locale directly if needed
    return fake


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


def create_random_address(fake=None, save=True, **values):
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


def create_random_company(shop=None):
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


def create_random_order(
    customer=None,
    products=(),
    completion_probability=0,
    shop=None,
    random_products=True,
    create_payment_for_order_total=False,
    order_date=None,
):
    if not customer:
        customer = Contact.objects.all().order_by("?").first()
    if not customer:
        raise ValueError("Error! No valid contacts.")
    if shop is None:
        shop = get_default_shop()
    pricing_context = _get_pricing_context(shop, customer)
    source = OrderSource(shop)
    source.customer = customer
    source.customer_comment = "Mock Order"
    # Confirmed: billing_address and shipping_address assignment works in Django 3+
    if getattr(customer, "default_billing_address", None) and getattr(customer, "default_shipping_address", None):
        source.billing_address = customer.default_billing_address
        source.shipping_address = customer.default_shipping_address
    else:
        source.billing_address = create_random_address()
        source.shipping_address = create_random_address()
    source.order_date = order_date or (now() - datetime.timedelta(days=random.uniform(0, 400)))
    source.status = get_initial_order_status()
    # Confirmed: Product.objects.listed() method works in Django 3+
    if not products:
        try:
            products = list(Product.objects.listed(source.shop, customer).order_by("?")[:40])
        except Exception:
            products = list(Product.objects.all().order_by("?")[:40])
    if random_products:
        quantity = random.randint(3, 10)
    else:
        quantity = len(products)
    for i in range(quantity):
        if random_products:
            product = random.choice(products)
        else:
            product = products[i]
        quantity = random.randint(1, 5)
        price_info = product.get_price_info(pricing_context, quantity=quantity)
        shop_product = product.get_shop_instance(source.shop)
        # Confirmed: ShopProduct.get_supplier() method works in Django 3+
        supplier = shop_product.get_supplier(source.customer, quantity, source.shipping_address)
        line = source.add_line(
            type=OrderLineType.PRODUCT,
            product=product,
            supplier=supplier,
            quantity=quantity,
            base_unit_price=price_info.base_unit_price,
            discount_amount=price_info.discount_amount,
            sku=product.sku,
            text=product.safe_translation_getter("name", any_language=True),
        )
        assert line.price == price_info.price
    with atomic():
        oc = OrderCreator()
        order = oc.create_order(source)
        if random.random() < completion_probability:
            # Confirmed: Order.lines attribute works in Django 3+
            try:
                suppliers = {line.supplier for line in order.lines.filter(supplier__isnull=False, quantity__gt=0)}
            except Exception:
                suppliers = set()
            for supplier in suppliers:
                order.create_shipment_of_all_products(supplier=supplier)
            if create_payment_for_order_total:
                order.create_payment(order.taxful_total_price)
            # also set complete
            order.save()
            # Confirmed: Contact.user attribute exists in Django 3+
            next_status = get_completed_order_status()
            if next_status is not None and hasattr(customer, "user"):
                order.change_status(next_status=next_status, user=customer.user)
        return order


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


def get_basket(shop=None):
    shop = shop or get_default_shop()
    return Basket.objects.create(
        key=uuid.uuid1().hex,
        shop=shop,
        prices_include_tax=shop.prices_include_tax,
        currency=shop.currency,
    )


def create_random_contact_group(shop=None):
    fake = get_faker(["job"])
    name = fake.format("job")
    identifier = "{}-{}".format(
        ContactGroup.objects.count() + 1,
        name.lower().replace(" ", "-"),
    )
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


def create_empty_order(prices_include_tax=False, shop=None):
    order = Order(
        shop=(shop or get_shop(prices_include_tax=prices_include_tax)),
        payment_method=get_default_payment_method(),
        shipping_method=get_default_shipping_method(),
        billing_address=get_address(name="Mony Doge").to_immutable(),
        shipping_address=get_address(name="Shippy Doge").to_immutable(),
        order_date=now(),
        status=get_initial_order_status(),
    )
    return order


def add_product_to_order(
    order,
    supplier,
    product,
    quantity,
    taxless_base_unit_price,
    tax_rate=0,
    pricing_context=None,
):
    if not pricing_context:
        pricing_context = _get_pricing_context(order.shop, order.customer)
    product_order_line = OrderLine(order=order)
    update_order_line_from_product(
        pricing_context,
        order_line=product_order_line,
        product=product,
        quantity=quantity,
        supplier=supplier,
    )
    base_unit_price = order.shop.create_price(taxless_base_unit_price)
    if order.prices_include_tax:
        base_unit_price *= 1 + tax_rate
    try:
        product_order_line.base_unit_price = order.shop.create_price(base_unit_price)
    except Exception:
        pass
    product_order_line.save()
    taxes = [get_test_tax(tax_rate)]
    price = quantity * base_unit_price
    taxed_price = stacked_value_added_taxes(price, taxes)
    order_line_tax = OrderLineTax.from_tax(
        taxes[0],
        taxed_price.taxless.amount,
        order_line=product_order_line,
    )
    order_line_tax.save()
    if hasattr(product_order_line, "taxes"):
        try:
            product_order_line.taxes.add(order_line_tax)
        except Exception:
            pass


def create_order_with_product(
    product,
    supplier,
    quantity,
    taxless_base_unit_price,
    tax_rate=0,
    n_lines=1,
    shop=None,
):
    order = create_empty_order(shop=shop)
    order.full_clean()
    order.save()

    pricing_context = _get_pricing_context(order.shop, order.customer)
    for _x in range(n_lines):
        add_product_to_order(
            order,
            supplier,
            product,
            quantity,
            taxless_base_unit_price,
            tax_rate,
            pricing_context,
        )

    assert order.get_product_ids_and_quantities()[product.pk] == (quantity * n_lines), "Things got added"
    order.cache_prices()
    order.save()
    return order


def create_package_product(sku, shop=None, supplier=None, default_price=None, children=4, **attrs):
    package_product = create_product(sku, shop, supplier, default_price, **attrs)
    assert not package_product.get_package_child_to_quantity_map()
    children = [create_product(f"PackageChild-{x}", shop=shop, supplier=supplier) for x in range(children)]
    package_def = {child: 1 + idx for (idx, child) in enumerate(children)}
    package_product.make_package(package_def)
    assert package_product.is_package_parent()
    package_product.save()
    return package_product
