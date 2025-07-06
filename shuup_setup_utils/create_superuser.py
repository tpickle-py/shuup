import os

import django
from django.contrib.auth import get_user_model


def create_superuser():
    """Create a default superuser if it doesn't already exist."""
    username = "admin"
    email = "admin@admin.com"
    password = "adm!nTHISNEED1"

    try:
        # Set the settings module to test_settings or your preferred settings
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shuup_workbench.settings.dev")
        django.setup()
        user_model = get_user_model()
        if not user_model.objects.filter(username=username).exists():
            user_model.objects.create_superuser(username, email, password)
            print(f"Superuser '{username}' created successfully.")
        else:
            print(f"Superuser '{username}' already exists.")
    except Exception as e:
        print(f"Error creating superuser: {e}")
        pass


if __name__ == "__main__":
    create_superuser()
