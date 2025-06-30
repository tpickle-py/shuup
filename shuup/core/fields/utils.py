import decimal

from shuup.core.fields import MONEY_FIELD_DECIMAL_PLACES


def ensure_decimal_places(value):
    return value.quantize(decimal.Decimal(".1") ** MONEY_FIELD_DECIMAL_PLACES)
