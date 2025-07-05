import datetime
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_nonzero_quantity(value):
    if value is not None and value < 0:
        raise ValidationError(_("Quantity must not be negative."))


def validate_purchase_multiple(value):
    if value < 0:
        raise ValidationError(_("Purchase multiple must be zero or a positive number."))


def validate_minimum_less_than_maximum(minimum, maximum):
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ValidationError(_("Minimum value cannot be greater than maximum value."))


def validate_future_date(value):
    if value is not None and value <= datetime.datetime.now():
        raise ValidationError(_("Date must be in the future."))


class StrongPasswordValidator:
    """
    Validates password strength with requirements for:
    - At least 8 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains digit
    - Contains special character
    """

    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least %(min_length)d characters long.") % {"min_length": self.min_length}
            )

        if not re.search(r"[A-Z]", password):
            raise ValidationError(_("Password must contain at least one uppercase letter."))

        if not re.search(r"[a-z]", password):
            raise ValidationError(_("Password must contain at least one lowercase letter."))

        if not re.search(r"[0-9]", password):
            raise ValidationError(_("Password must contain at least one digit."))

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(_('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).'))

    def get_help_text(self):
        return _(
            "Your password must contain at least %(min_length)d characters, "
            "including uppercase and lowercase letters, digits, and special characters."
        ) % {"min_length": self.min_length}
