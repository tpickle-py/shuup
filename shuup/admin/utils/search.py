import re

from shuup.utils.django_compat import force_text


class FuzzyMatcher:
    def __init__(self, query):
        bits = [re.escape(bit.strip()) for bit in query.split() if bit.strip()]
        self.regexp = re.compile(".+".join(bits), re.I)

    def test(self, text):
        return bool(self.regexp.search(force_text(text)))


def split_query(query_string, minimum_part_length=3):
    """
    Split a string into a set of non-empty words, none shorter than `minimum_part_length` characters.

    :param query_string: Query string
    :type query_string: str
    :param minimum_part_length: Minimum part length
    :type minimum_part_length: int
    :return: Set of query parts
    :rtype: set[str]
    """
    query_string = force_text(query_string)
    return {
        part
        for part in (part.strip() for part in query_string.split())
        if len(part) >= minimum_part_length
    }
