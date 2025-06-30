from django.utils.translation import get_language

from shuup.core.models import Product, ProductAttribute
from shuup.utils.translation import cache_translations


def cache_product_things(request, products, language=None, attribute_identifiers=[]):
    # Cache necessary things for products. WARNING: This will cause queryset iteration.
    language = language or get_language()
    if attribute_identifiers:
        Product.cache_attributes_for_targets(
            ProductAttribute,
            products,
            attribute_identifiers=attribute_identifiers,
            language=language,
        )
    products = cache_translations(products, (language,))
    return products
