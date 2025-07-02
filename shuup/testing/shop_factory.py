import factory
import factory.fuzzy as fuzzy
from factory.django import DjangoModelFactory

from shuup.core.models import Shop

from .person_contact_factory import PersonContactFactory


class ShopFactory(DjangoModelFactory):
    class Meta:
        model = Shop

    name = fuzzy.FuzzyText(prefix="A Very nice shop ")
    owner = factory.SubFactory(PersonContactFactory)
