from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify

from shuup.utils.django_compat import force_text


def generate_multilanguage_slugs(object, name_getter, slug_length=128):
    translations_model = object._parler_meta.root_model
    for language_code, _language_name in settings.LANGUAGES:
        try:
            translation = object.get_translation(language_code=language_code)
            translation.refresh_from_db()
        except ObjectDoesNotExist:
            # For some reason the `get_translation` raises if the object is created recently
            translation = translations_model.objects.filter(master_id=object.id, language_code=language_code).first()
            if not translation:
                # Guessing the translation is deleted recently so let's just skip this language
                continue

        # Since slugs can be set by the merchant let's not override if already set
        if not translation or translation.slug:
            continue

        name = force_text(name_getter(object, translation))
        slug = slugify(name)
        translation.slug = slug[:slug_length] if slug else None
        translation.save()
