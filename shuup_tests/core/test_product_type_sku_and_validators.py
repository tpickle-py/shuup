import datetime

from django.core.exceptions import ValidationError

import pytest

from shuup.core import validators
from shuup.core.models import Product, ProductType
from shuup.testing.factories import (
    get_default_product_type,
    get_default_sales_unit,
    get_default_shop,
    get_default_supplier,
)
from shuup.testing.factories.tax_factory import get_default_tax_class


@pytest.mark.django_db
def test_product_type_sku_uniqueness():
    shop = get_default_shop()
    _supplier = get_default_supplier(shop)
    product_type = get_default_product_type()
    sku = "unique-sku"
    _default_price = shop.create_price(1)
    get_sales_unit = get_default_sales_unit
    product_attrs = {
        "type": product_type,
        "tax_class": get_default_tax_class(),
        "sku": sku,
        "width": 100,
        "height": 100,
        "depth": 100,
        "net_weight": 100,
        "gross_weight": 100,
        "sales_unit": get_sales_unit(),
    }

    # Create first product
    _product1 = Product.objects.create(name="Product 1", **product_attrs)

    # Attempt to create second product with same type and sku
    product2 = Product(name="Product 2", **product_attrs)
    with pytest.raises(ValidationError):
        product2.full_clean()


def test_validate_nonzero_quantity():
    validators.validate_nonzero_quantity(1)  # Should not raise
    with pytest.raises(ValidationError):
        validators.validate_nonzero_quantity(0)


def test_validate_purchase_multiple():
    validators.validate_purchase_multiple(0)  # Should not raise
    validators.validate_purchase_multiple(2)  # Should not raise
    with pytest.raises(ValidationError):
        validators.validate_purchase_multiple(-1)


def test_validate_minimum_less_than_maximum():
    validators.validate_minimum_less_than_maximum(1, 2)  # Should not raise
    validators.validate_minimum_less_than_maximum(None, 2)  # Should not raise
    validators.validate_minimum_less_than_maximum(1, None)  # Should not raise
    with pytest.raises(ValidationError):
        validators.validate_minimum_less_than_maximum(3, 2)


def test_validate_future_date():
    future = datetime.datetime.now() + datetime.timedelta(days=1)
    past = datetime.datetime.now() - datetime.timedelta(days=1)
    validators.validate_future_date(future)  # Should not raise
    validators.validate_future_date(None)  # Should not raise
    with pytest.raises(ValidationError):
        validators.validate_future_date(past)
