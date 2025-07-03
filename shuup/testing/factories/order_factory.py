# Order-related factory functions
import datetime
import random
import uuid

from django.db.transaction import atomic
from django.utils.timezone import now

from shuup.core.defaults.order_statuses import create_default_order_statuses
from shuup.core.models import (
    Basket,
    Contact,
    Order,
    OrderLine,
    OrderLineTax,
    OrderLineType,
    OrderStatus,
    Product,
)
from shuup.core.order_creator import OrderCreator, OrderSource
from shuup.core.shortcuts import update_order_line_from_product
from shuup.core.taxing.utils import stacked_value_added_taxes

from .shared import _get_pricing_context, create_random_address, get_address, get_default_shop


def get_initial_order_status():
    create_default_order_statuses()
    return OrderStatus.objects.get_default_initial()


def get_completed_order_status():
    create_default_order_statuses()
    return OrderStatus.objects.get_default_complete()


def create_random_order(
    customer=None,
    products=(),
    completion_probability=0,
    shop=None,
    random_products=True,
    create_payment_for_order_total=False,
    order_date=None,
) -> Order:
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
    default_billing_address = getattr(customer, "default_billing_address", None)
    default_shipping_address = getattr(customer, "default_shipping_address", None)
    if default_billing_address:
        source.billing_address = customer.default_billing_address
    if default_shipping_address:
        source.shipping_address = customer.default_shipping_address
    if not source.billing_address or not source.shipping_address:
        source.billing_address = create_random_address()
        source.shipping_address = create_random_address()
    source.order_date = order_date or (now() - datetime.timedelta(days=random.uniform(0, 400)))
    source.status = get_initial_order_status()
    if not products:
        try:
            products = list(Product.objects.listed(source.shop, customer).order_by("?")[:40])
        except Exception:
            products = list(Product.objects.all().order_by("?")[:40])
    if random_products:
        num_lines = random.randint(3, 10)
    else:
        num_lines = len(products)
    for i in range(num_lines):
        if random_products:
            product = random.choice(products)
        else:
            product = products[i]
        line_quantity = random.randint(1, 5)
        price_info = product.get_price_info(pricing_context, quantity=line_quantity)
        shop_product = product.get_shop_instance(source.shop)
        supplier = shop_product.get_supplier(source.customer, line_quantity, source.shipping_address)
        line = source.add_line(
            type=OrderLineType.PRODUCT,
            product=product,
            supplier=supplier,
            quantity=line_quantity,
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
            lines = getattr(order, "lines", None)
            if not lines:
                raise ValueError("Order has no lines to complete.")
            suppliers = {line.supplier for line in lines.filter(supplier__isnull=False, quantity__gt=0)}
            for supplier in suppliers:
                order.create_shipment_of_all_products(supplier=supplier)
            if create_payment_for_order_total:
                order.create_payment(order.taxful_total_price)
            order.save()
            next_status = get_completed_order_status()
            user = getattr(customer, "user", None)
            if next_status is not None and user and hasattr(customer, "user"):
                order.change_status(next_status=next_status, user=user)
        return order


def create_empty_order(prices_include_tax=False, shop=None):
    from .service_factory import get_default_payment_method, get_default_shipping_method
    from .shared import get_shop

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
    from .tax_factory import get_test_tax

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


def get_basket(shop=None):
    shop = shop or get_default_shop()
    return Basket.objects.create(
        key=uuid.uuid1().hex,
        shop=shop,
        prices_include_tax=shop.prices_include_tax,
        currency=shop.currency,
    )
