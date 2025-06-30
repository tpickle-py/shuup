

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import translation

from shuup.testing.mock_population import Populator


class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--with-superuser", default=None)

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGES[0][0])
        superuser_name = options.get("with_superuser")
        if superuser_name:
            filter_params = {get_user_model().USERNAME_FIELD: superuser_name}
            user = get_user_model().objects.filter(**filter_params).first()
            if not user:
                user = get_user_model().objects.create_superuser(
                    username=superuser_name,
                    email="{}@shuup.local".format(superuser_name),
                    password=superuser_name,
                )
                print("Superuser created: %s" % user)  # noqa
            else:
                print("Superuser pre-existed: %s" % user)  # noqa
        Populator().populate()
