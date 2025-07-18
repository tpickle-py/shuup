import datetime

from django.conf import settings

from shuup import configuration
from shuup.core.constants import (
    ORDER_REFERENCE_NUMBER_LENGTH_FIELD,
    ORDER_REFERENCE_NUMBER_METHOD_FIELD,
    ORDER_REFERENCE_NUMBER_PREFIX_FIELD,
)
from shuup.utils.django_compat import force_text
from shuup.utils.importing import load

from ._counters import Counter, CounterType


def calc_reference_number_checksum(rn):
    muls = (7, 3, 1)
    s = 0
    for i, ch in enumerate(rn[::-1]):
        s += muls[i % 3] * int(ch)
    s = 10 - (s % 10)
    return force_text(s)[-1]


def get_unique_reference_number(shop, id):
    now = datetime.datetime.now()
    ref_length = configuration.get(
        shop,
        ORDER_REFERENCE_NUMBER_LENGTH_FIELD,
        settings.SHUUP_REFERENCE_NUMBER_LENGTH,
    )
    dt = (f"{now.strftime('%y%m%d'):0>6}{now.microsecond:07d}{id % 1000:04d}").rjust(
        ref_length,  # type: ignore
        "0",
    )
    return dt + calc_reference_number_checksum(dt)


def get_unique_reference_number_for_order(order):
    return get_unique_reference_number(order.shop, order.pk)


def get_running_reference_number(order):
    value = Counter.get_and_increment(CounterType.ORDER_REFERENCE)
    prefix = "{}".format(
        configuration.get(
            order.shop,
            ORDER_REFERENCE_NUMBER_PREFIX_FIELD,
            settings.SHUUP_REFERENCE_NUMBER_PREFIX,
        )
    )
    ref_length = configuration.get(
        order.shop,
        ORDER_REFERENCE_NUMBER_LENGTH_FIELD,
        settings.SHUUP_REFERENCE_NUMBER_LENGTH,
    )

    padded_value = force_text(value).rjust(ref_length - len(prefix), "0")  # type: ignore
    reference_no = f"{prefix}{padded_value}"
    return reference_no + calc_reference_number_checksum(reference_no)


def get_shop_running_reference_number(order):
    value = Counter.get_and_increment(CounterType.ORDER_REFERENCE)
    prefix = f"{order.shop.pk:06d}"
    ref_length = configuration.get(
        order.shop,
        ORDER_REFERENCE_NUMBER_LENGTH_FIELD,
        settings.SHUUP_REFERENCE_NUMBER_LENGTH,
    )
    padded_value = force_text(value).rjust(ref_length - len(prefix), "0")  # type: ignore
    reference_no = f"{prefix}{padded_value}"
    return reference_no + calc_reference_number_checksum(reference_no)


def get_reference_number(order):
    if order.reference_number:
        raise ValueError("Error! Order passed to function `get_reference_number()` already has a reference number.")
    reference_number_method = configuration.get(
        order.shop,
        ORDER_REFERENCE_NUMBER_METHOD_FIELD,
        settings.SHUUP_REFERENCE_NUMBER_METHOD,
    )
    if reference_number_method == "unique":
        return get_unique_reference_number_for_order(order)
    elif reference_number_method == "running":
        return get_running_reference_number(order)
    elif reference_number_method == "shop_running":
        return get_shop_running_reference_number(order)
    elif callable(reference_number_method):
        return reference_number_method(order)
    else:
        getter = load(reference_number_method, "Reference number generator")
        return getter(order)


def get_order_identifier(order):
    if order.identifier:
        raise ValueError("Error! Order passed to function `get_order_identifier()` already has an identifier.")
    order_identifier_method = settings.SHUUP_ORDER_IDENTIFIER_METHOD
    if order_identifier_method == "id":
        return force_text(order.id)
    elif callable(order_identifier_method):
        return order_identifier_method(order)
    else:
        getter = load(order_identifier_method, "Order identifier generator")
        return getter(order)
