import factory.fuzzy as fuzzy
from factory.django import DjangoModelFactory

from shuup.core.models import SalesUnit


class SalesUnitFactory(DjangoModelFactory):
    class Meta:
        model = SalesUnit

    name = fuzzy.FuzzyText(length=12, prefix="Sales Unit ")
    symbol = fuzzy.FuzzyText(length=6, prefix="SU ")
