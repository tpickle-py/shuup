import hashlib
import os

import six
from django.conf import settings
from django_jinja import library
from easy_thumbnails.alias import aliases
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.templatetags.thumbnail import RE_SIZE

from shuup.core import cache


def process_thumbnailer_options(kwargs):
    default_options = getattr(settings, "THUMBNAIL_DEFAULT_OPTIONS", {})
    options = {}
    options.update(default_options)
    options.update(kwargs)
    size = options.setdefault("size", (128, 128))
    if isinstance(size, six.text_type):
        m = RE_SIZE.match(size)
        if m:
            options["size"] = (int(m.group(1)), int(m.group(2)))
        else:
            raise ValueError("Error! %r is not a valid size." % size)
    return options


def _get_cached_thumbnail_url(source, **kwargs):
    from filer.models.filemodels import File

    from shuup.core.models import ProductMedia

    sorted_items = dict(sorted(kwargs.items(), key=lambda item: item[0]))
    kwargs_hash = hashlib.sha1(str(sorted_items).encode("utf-8")).hexdigest()
    cache_key = None

    if isinstance(source, (File, ProductMedia)) and source.pk:
        cache_key = f"thumbnail_{source.pk}_{source.__class__.__name__}:_cached_thumbnail_{kwargs_hash}"

    elif isinstance(source, six.string_types):
        cache_key = f"_cached_thumbnail_url_{kwargs_hash}"

    elif hasattr(source, "url") and source.url:
        cache_key = f"_cached_thumbnail_url_{source.url}"

    if cache_key:
        return cache_key, cache.get(cache_key)
    return (None, None)


@library.filter
def thumbnail(source, alias=None, generate=True, **kwargs):
    if not source:
        return None

    cache_key, cached_thumbnail_url = _get_cached_thumbnail_url(
        source, alias=alias, generate=generate, **kwargs
    )

    if cached_thumbnail_url is not None:
        return cached_thumbnail_url

    thumbnailer_instance = get_thumbnailer(source)

    if not thumbnailer_instance:
        return None

    if _is_svg(thumbnailer_instance):
        return source.url if hasattr(source, "url") else None

    if alias:
        options = aliases.get(alias, target=thumbnailer_instance.alias_target)
        options.update(process_thumbnailer_options(kwargs))
    else:
        options = process_thumbnailer_options(kwargs)

    try:
        thumbnail_instance = thumbnailer_instance.get_thumbnail(
            options, generate=generate
        )
        thumbnail_url = thumbnail_instance.url
        if cache_key:
            cache.set(cache_key, thumbnail_url)
        return thumbnail_url
    except (OSError, InvalidImageFormatError, ValueError):
        return None


def _is_svg(thumbnailer_instance):
    file_name = getattr(thumbnailer_instance, "name", None)
    if not file_name:
        return False
    return bool(os.path.splitext(file_name)[1].lower() == ".svg")


@library.filter
def thumbnailer(source):
    return get_thumbnailer(source)
