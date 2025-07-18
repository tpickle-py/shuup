import datetime
from typing import Iterable

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from shuup.admin.modules.products.issues import ProductValidationIssue
from shuup.core.models import Shop, ShopProduct, Supplier


class AdminProductValidator:
    """Base class for validating products."""

    ordering = 0

    def get_validation_issues(
        self,
        _shop_product: ShopProduct,
        _shop: Shop,
        _user,
        _supplier: Supplier = None,  # type: ignore
    ) -> Iterable[ProductValidationIssue]:
        return []  # Empty iterable instead of yielding None


def validate_nonzero_quantity(value):
    if value == 0:
        raise ValidationError(_("Quantity must not be zero."))


def validate_positive_quantity(value):
    if value <= 0:
        raise ValidationError(_("Quantity must be a positive number."))


def validate_purchase_multiple(value):
    if value < 0:
        raise ValidationError(_("Purchase multiple must be zero or a positive number."))


def validate_minimum_less_than_maximum(minimum, maximum):
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ValidationError(_("Minimum value cannot be greater than maximum value."))


def validate_future_date(value):
    if value is not None and value <= datetime.datetime.now():
        raise ValidationError(_("Date must be in the future."))
