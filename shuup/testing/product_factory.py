import factory
import factory.fuzzy as fuzzy
from factory.django import DjangoModelFactory

from shuup.core.models import Product
from shuup.testing.text_data import random_title

from . import get_default_product_type, get_default_sales_unit, get_default_tax_class


class FuzzyName(fuzzy.FuzzyText):
    def fuzz(self):
        return random_title(prefix=self.prefix, suffix=self.suffix)


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    type = factory.LazyAttribute(lambda obj: get_default_product_type())
    sku = fuzzy.FuzzyText(length=10)
    sales_unit = factory.LazyAttribute(lambda obj: get_default_sales_unit())
    tax_class = factory.LazyAttribute(lambda obj: get_default_tax_class())
    profit_center = fuzzy.FuzzyInteger(10000, 99999)
    cost_center = fuzzy.FuzzyInteger(10000, 99999)
    name = FuzzyName()

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        # ...existing code for image and ShopProduct creation...
        pass
