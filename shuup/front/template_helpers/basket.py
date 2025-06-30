from typing import Iterable

from shuup.core.order_creator import SourceLine
from shuup.front.utils.order_source import LineProperty, get_line_properties


def get_properties_from_line(line: SourceLine) -> Iterable[LineProperty]:
    return list(get_line_properties(line))
