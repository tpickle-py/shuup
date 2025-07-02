import factory
import factory.fuzzy as fuzzy
from factory.django import DjangoModelFactory

from shuup.core.models import CompanyContact


class CompanyFactory(DjangoModelFactory):
    class Meta:
        model = CompanyContact

    name = fuzzy.FuzzyText()
    tax_number = fuzzy.FuzzyText()
    email = factory.Sequence(lambda n: f"company{n}@example.shuup.com")
