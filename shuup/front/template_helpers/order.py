from typing import Iterable

from shuup.core.models import OrderLine
from shuup.front.utils.order_source import LineProperty, get_line_properties


def get_properties_from_line(line: OrderLine) -> Iterable[LineProperty]:
    return list(get_line_properties(line))
