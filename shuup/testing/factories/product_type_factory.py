import factory
import factory.fuzzy as fuzzy
from factory.django import DjangoModelFactory

from shuup.core.models import ProductType


class ProductTypeFactory(DjangoModelFactory):
    class Meta:
        model = ProductType

    identifier = factory.Sequence(lambda n: f"type_{n}")
    name = fuzzy.FuzzyText(length=6, prefix="Product Type ")
