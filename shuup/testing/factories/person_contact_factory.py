import factory

from shuup.core.models import PersonContact


class PersonContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PersonContact

    email = factory.Sequence(lambda n: f"person{n}@example.shuup.com")
    name = factory.Faker("name")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    phone = factory.Faker("phone_number")
    gender = factory.Iterator(["m", "f", "u", "o"])
    language = "en"
