"""
"Tagged JSON" encoder/decoder.

Objects that are normally not unambiguously representable via JSON
are encoded into special objects of the form `{tag: val}`; the encoding
and decoding process can be customized however necessary.
"""

import datetime
import decimal
from enum import Enum

import django.utils.dateparse as dateparse
from django.core.exceptions import ImproperlyConfigured
from jsonfield.encoder import JSONEncoder
from six import text_type

from shuup.compat import six
from shuup.utils.importing import load
from shuup.utils.iterables import first


def isoformat(obj):
    return obj.isoformat()


def encode_enum(enum_val):
    enum_cls = enum_val.__class__
    spec = f"{enum_cls.__module__}:{enum_cls.__name__}"
    try:
        if load(spec) != enum_cls:
            raise ImproperlyConfigured("Error! That's not the same class.")
    except ImproperlyConfigured:  # Also raised by `load`
        return enum_val.value  # Fall back to the bare value.
    return [spec, enum_val.value]


def decode_enum(val):
    spec, value = val
    cls = load(spec)
    if issubclass(cls, Enum):
        return cls(value)
    return value  # Fall back to the bare value. Not optimal, I know.


class TagRegistry:
    def __init__(self):
        self.tags = {}

    def register(self, tag, classes, encoder=text_type, decoder=None):
        if decoder is None:
            if isinstance(classes, (list, tuple)):
                decoder = classes[0]
            else:
                decoder = classes
        if not callable(decoder):
            raise ValueError(f"Error! Decoder `{decoder!r}` for tag `{tag!r}` is not callable.")
        if not callable(encoder):
            raise ValueError(f"Error! Encoder `{encoder!r}` for tag `{tag!r}` is not callable.")

        self.tags[tag] = {"classes": classes, "encoder": encoder, "decoder": decoder}

    def encode(self, obj, default):
        for tag, info in six.iteritems(self.tags):
            if isinstance(obj, info["classes"]):
                return {tag: info["encoder"](obj)}
        return default(obj)

    def decode(self, obj):
        if len(obj) == 1:
            tag, val = first(obj.items())
            info = self.tags.get(tag)
            if info:
                return info["decoder"](val)
        return obj


#: The default tag registry.
tag_registry = TagRegistry()
tag_registry.register("$datetime", datetime.datetime, encoder=isoformat, decoder=dateparse.parse_datetime)
tag_registry.register("$date", datetime.date, encoder=isoformat, decoder=dateparse.parse_date)
tag_registry.register("$time", datetime.time, encoder=isoformat, decoder=dateparse.parse_time)
tag_registry.register("$dec", decimal.Decimal)
tag_registry.register("$enum", Enum, encoder=encode_enum, decoder=decode_enum)


class TaggedJSONEncoder(JSONEncoder):
    registry = tag_registry

    def default(self, obj):
        return self.registry.encode(obj, super(JSONEncoder, self).default)
