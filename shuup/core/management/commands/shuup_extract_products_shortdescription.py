"""
Extract products short description from the current description.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = __doc__.strip()

    def handle(self, *args, **options):
        from django.conf import settings
        from jinja2.filters import do_striptags

        from shuup.core.models import Product

        for product in Product.objects.all():
            for lang, _ in settings.LANGUAGES:
                product_translation = product.translations.filter(master_id=product.pk, language_code=lang).first()

                if product_translation and product_translation.description:
                    product_translation.short_description = do_striptags(product_translation.description)[:150]
                    product_translation.save()

        self.stdout.write("Done.")
