
from django.conf import settings
from django.dispatch import Signal
from registration.signals import login_user

company_contact_activated = Signal(
    providing_args=["instance", "request"], use_caching=True
)

# Used when admin reactivates an account
user_reactivated = Signal(providing_args=["user", "request"])


def handle_user_activation(user, **kwargs):
    activate_contact_by_user(user)
    if settings.REGISTRATION_AUTO_LOGIN:
        login_user(user=user, **kwargs)


def activate_contact_by_user(user, **kwargs):
    contact = user.contact
    contact.is_active = user.is_active
    contact.save(update_fields=("is_active",))
