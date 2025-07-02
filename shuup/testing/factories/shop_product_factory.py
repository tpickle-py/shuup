import factory
import factory.fuzzy as fuzzy
from factory.django import DjangoModelFactory

from shuup.core.models import ShopProduct

from .product_factory import ProductFactory
from .shop_factory import ShopFactory


class ShopProductFactory(DjangoModelFactory):
    shop = factory.SubFactory(ShopFactory)
    product = factory.SubFactory(ProductFactory)

    class Meta:
        model = ShopProduct

    purchasable = fuzzy.FuzzyAttribute(lambda: True)
    visibility = fuzzy.FuzzyChoice(
        [
            0,  # NOT_VISIBLE
            1,  # LISTED
            2,  # SEARCHABLE
            3,  # ALWAYS_VISIBLE
        ]
    )
    default_price_value = fuzzy.FuzzyDecimal(0, 500)

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        # ...existing code for post-processing...
        pass
