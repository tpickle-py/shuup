import factory
import factory.fuzzy as fuzzy
from factory.django import DjangoModelFactory

from shuup.core.models import Category, CategoryStatus


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    identifier = factory.Sequence(lambda n: f"category{n}")
    name = fuzzy.FuzzyText(length=6, prefix="Category ")
    status = fuzzy.FuzzyChoice(
        [
            CategoryStatus.INVISIBLE,
            CategoryStatus.VISIBLE,
            CategoryStatus.VISIBLE,
        ]
    )
