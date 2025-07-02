import factory
import factory.fuzzy as fuzzy
from django.conf import settings
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: f"user{n}")  # type: ignore
    email = factory.Sequence(lambda n: f"user{n}@example.shuup.com")  # type: ignore
    password = factory.PostGenerationMethodCall("set_password", "test")  # type: ignore
    first_name = fuzzy.FuzzyText(length=4, prefix="First Name ")
    last_name = fuzzy.FuzzyText(length=4, prefix="Last Name ")
