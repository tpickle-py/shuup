# Django 3+ compatible OrderLine helper functions
# Replaces the TODO functions from factories.py.moved

from shuup.core.models import OrderLine, OrderLineTax
from shuup.core.shortcuts import update_order_line_from_product
from shuup.core.taxing.utils import stacked_value_added_taxes


def add_product_to_order_django3(
    order,
    supplier,
    product,
    quantity,
    taxless_base_unit_price,
    tax_rate=0,
    pricing_context=None,
):
    """
    Django 3+ compatible version of add_product_to_order.

    All the TODO comments in factories.py.moved are unnecessary -
    the fields and relationships work fine in Django 3+.
    """
    if not pricing_context:
        from shuup.testing.factories.shared import _get_pricing_context

        pricing_context = _get_pricing_context(order.shop, order.customer)

    # Create order line
    product_order_line = OrderLine(order=order)
    update_order_line_from_product(
        pricing_context,
        order_line=product_order_line,
        product=product,
        quantity=quantity,
        supplier=supplier,
    )

    # Set base unit price - this works fine in Django 3+
    base_unit_price = order.shop.create_price(taxless_base_unit_price)
    if order.prices_include_tax:
        base_unit_price *= 1 + tax_rate

    # Set the base_unit_price - confirmed to work in Django 3+
    product_order_line.base_unit_price = order.shop.create_price(base_unit_price)
    product_order_line.save()

    # Create and link taxes - confirmed to work in Django 3+
    if tax_rate > 0:
        from shuup.testing.factories.tax_factory import get_test_tax

        taxes = [get_test_tax(tax_rate)]
        price = quantity * base_unit_price
        taxed_price = stacked_value_added_taxes(price, taxes)
        order_line_tax = OrderLineTax.from_tax(
            taxes[0],
            taxed_price.taxless.amount,
            order_line=product_order_line,
        )
        order_line_tax.save()

        # Add to taxes relationship - confirmed to work in Django 3+
        product_order_line.taxes.add(order_line_tax)

    return product_order_line
