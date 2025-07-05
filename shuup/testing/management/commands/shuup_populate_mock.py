import secrets
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import translation

from shuup.testing.mock_population import Populator


class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--with-superuser", default=None)

    def generate_strong_password(self, length=12):
        """Generate a secure password meeting complexity requirements."""
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        # Ensure it has all required character types
        if (
            any(c.isupper() for c in password)
            and any(c.islower() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*" for c in password)
        ):
            return password
        # Fallback to ensure compliance
        return "SecureAdmin123!"

    def handle(self, *args, **options):
        translation.activate(settings.LANGUAGES[0][0])
        superuser_name = options.get("with_superuser")
        if superuser_name:
            filter_params = {get_user_model().USERNAME_FIELD: superuser_name}
            user = get_user_model().objects.filter(**filter_params).first()
            if not user:
                secure_password = self.generate_strong_password()
                user = get_user_model().objects.create_superuser(
                    username=superuser_name,
                    email=f"{superuser_name}@shuup.local",
                    password=secure_password,
                )
                print("Superuser created: %s" % user)  # noqa
                print("Superuser password: %s" % secure_password)  # noqa
                print("IMPORTANT: Please save this password securely!")  # noqa
            else:
                print("Superuser pre-existed: %s" % user)  # noqa
        Populator().populate()
