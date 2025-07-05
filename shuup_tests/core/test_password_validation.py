import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.test.client import RequestFactory

from shuup.core.validators import StrongPasswordValidator
from shuup.front.apps.registration.forms import UserCreationForm, PersonRegistrationForm
from shuup.testing import factories
from shuup.testing.utils import apply_request_middleware

User = get_user_model()


class TestStrongPasswordValidator(TestCase):
    """Test the custom StrongPasswordValidator."""

    def setUp(self):
        self.validator = StrongPasswordValidator()
        self.user = factories.create_random_user()

    def test_valid_strong_password(self):
        """Test that a strong password passes validation."""
        strong_passwords = ["Password123!", "SecureP@ss123", "MyStr0ng!Password", "Complex1@Pass"]

        for password in strong_passwords:
            try:
                self.validator.validate(password, self.user)
            except ValidationError:
                self.fail(f"Strong password '{password}' should pass validation")

    def test_password_too_short(self):
        """Test that short passwords are rejected."""
        short_passwords = ["P@ss1", "Sh0rt!", "12345"]

        for password in short_passwords:
            with self.assertRaises(ValidationError):
                self.validator.validate(password, self.user)

    def test_password_missing_uppercase(self):
        """Test that passwords without uppercase letters are rejected."""
        no_uppercase_passwords = ["password123!", "lowercase1@", "no_uppercase_here123!"]

        for password in no_uppercase_passwords:
            with self.assertRaises(ValidationError):
                self.validator.validate(password, self.user)

    def test_password_missing_lowercase(self):
        """Test that passwords without lowercase letters are rejected."""
        no_lowercase_passwords = ["PASSWORD123!", "UPPERCASE1@", "NO_LOWERCASE_HERE123!"]

        for password in no_lowercase_passwords:
            with self.assertRaises(ValidationError):
                self.validator.validate(password, self.user)

    def test_password_missing_digit(self):
        """Test that passwords without digits are rejected."""
        no_digit_passwords = ["Password!", "NoDigits@Here", "OnlyLetters!"]

        for password in no_digit_passwords:
            with self.assertRaises(ValidationError):
                self.validator.validate(password, self.user)

    def test_password_missing_special_character(self):
        """Test that passwords without special characters are rejected."""
        no_special_passwords = ["Password123", "NoSpecialChars1", "OnlyAlphaNum123"]

        for password in no_special_passwords:
            with self.assertRaises(ValidationError):
                self.validator.validate(password, self.user)

    def test_get_help_text(self):
        """Test that help text is properly formatted."""
        help_text = self.validator.get_help_text()
        self.assertIn("8 characters", help_text)
        self.assertIn("uppercase", help_text)
        self.assertIn("lowercase", help_text)
        self.assertIn("digits", help_text)
        self.assertIn("special characters", help_text)


@override_settings(
    AUTH_PASSWORD_VALIDATORS=[
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
            "OPTIONS": {
                "min_length": 8,
            },
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
        {
            "NAME": "shuup.core.validators.StrongPasswordValidator",
        },
    ]
)
class TestPasswordValidationIntegration(TestCase):
    """Test password validation with Django's validate_password function."""

    def setUp(self):
        self.user = factories.create_random_user()

    def test_weak_passwords_rejected(self):
        """Test that various weak passwords are rejected."""
        weak_passwords = [
            "1234",  # Too short, numeric only
            "password",  # Common password, no uppercase/digit/special
            "12345678",  # All digits, no letters/special
            "Password",  # Missing digit and special character
            "password123",  # Missing uppercase and special character
            "PASSWORD123",  # Missing lowercase and special character
            "Password!",  # Missing digit
            "password123!",  # Missing uppercase
            "PASSWORD123!",  # Missing lowercase
            "john",  # Too short, similar to user attributes
            "qwerty",  # Common weak password
            "admin",  # Common weak password
            "letmein",  # Common weak password
            "welcome",  # Common weak password
        ]

        for password in weak_passwords:
            with self.assertRaises(ValidationError, msg=f"Weak password '{password}' should be rejected"):
                validate_password(password, self.user)

    def test_strong_passwords_accepted(self):
        """Test that strong passwords are accepted."""
        strong_passwords = ["SecureP@ssw0rd!", "MyStr0ng!Pass", "C0mplex#Password", "V3ryS3cur3!", "Rand0m&Secure123"]

        for password in strong_passwords:
            try:
                validate_password(password, self.user)
            except ValidationError as e:
                self.fail(f"Strong password '{password}' should be accepted, but got: {e}")


class TestUserCreationFormValidation(TestCase):
    """Test password validation in user creation forms."""

    def test_weak_password_rejected_in_form(self):
        """Test that weak passwords are rejected in UserCreationForm."""
        form_data = {"username": "testuser", "password1": "weak", "password2": "weak"}
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_strong_password_accepted_in_form(self):
        """Test that strong passwords are accepted in UserCreationForm."""
        form_data = {"username": "testuser", "password1": "StrongP@ssw0rd123", "password2": "StrongP@ssw0rd123"}
        form = UserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")

    def test_password_mismatch(self):
        """Test that mismatched passwords are rejected."""
        form_data = {"username": "testuser", "password1": "StrongP@ssw0rd123", "password2": "DifferentP@ssw0rd123"}
        form = UserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class TestPersonRegistrationFormValidation(TestCase):
    """Test password validation in person registration forms."""

    def setUp(self):
        self.shop = factories.get_default_shop()
        rf = RequestFactory()
        self.request = apply_request_middleware(rf.get("/"))
        self.request.shop = self.shop

    def test_weak_password_rejected_in_person_form(self):
        """Test that weak passwords are rejected in PersonRegistrationForm."""
        form_data = {"username": "testuser", "email": "test@example.com", "password1": "weak", "password2": "weak"}
        form = PersonRegistrationForm(data=form_data, request=self.request)
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)

    def test_strong_password_accepted_in_person_form(self):
        """Test that strong passwords are accepted in PersonRegistrationForm."""
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongP@ssw0rd123",
            "password2": "StrongP@ssw0rd123",
        }
        form = PersonRegistrationForm(data=form_data, request=self.request)
        self.assertTrue(form.is_valid(), msg=f"Form errors: {form.errors}")


class TestWeakPasswordRejection(TestCase):
    """Comprehensive test for weak password rejection scenarios from GitHub issue #2642."""

    def setUp(self):
        self.shop = factories.get_default_shop()
        rf = RequestFactory()
        self.request = apply_request_middleware(rf.get("/"))
        self.request.shop = self.shop
        self.user = factories.create_random_user()

    def test_issue_2642_examples(self):
        """Test specific weak password examples mentioned in the GitHub issue."""
        # Examples from the security vulnerability report
        issue_examples = ["1234", "12345", "123456", "password", "admin", "test", "user", "guest"]

        for weak_password in issue_examples:
            with self.assertRaises(ValidationError, msg=f"GitHub issue example '{weak_password}' should be rejected"):
                validate_password(weak_password, self.user)

    def test_brute_force_vulnerable_passwords(self):
        """Test passwords vulnerable to brute force attacks."""
        vulnerable_passwords = ["a", "aa", "123", "abc", "qwe", "asd", "111", "000", "999"]

        for password in vulnerable_passwords:
            with self.assertRaises(
                ValidationError, msg=f"Brute-force vulnerable password '{password}' should be rejected"
            ):
                validate_password(password, self.user)

    def test_dictionary_attack_passwords(self):
        """Test common dictionary words that should be rejected."""
        dictionary_passwords = [
            "password",
            "welcome",
            "letmein",
            "monkey",
            "sunshine",
            "shadow",
            "master",
            "freedom",
            "whatever",
            "football",
        ]

        for password in dictionary_passwords:
            with self.assertRaises(ValidationError, msg=f"Dictionary word '{password}' should be rejected"):
                validate_password(password, self.user)

    def test_registration_form_rejects_weak_passwords(self):
        """Test that registration forms properly reject weak passwords from the issue."""
        weak_passwords = ["1234", "password", "admin", "test"]

        for weak_password in weak_passwords:
            # Test UserCreationForm
            form_data = {"username": "testuser", "password1": weak_password, "password2": weak_password}
            form = UserCreationForm(data=form_data)
            self.assertFalse(form.is_valid(), f"UserCreationForm should reject '{weak_password}'")

            # Test PersonRegistrationForm
            person_form_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password1": weak_password,
                "password2": weak_password,
            }
            person_form = PersonRegistrationForm(data=person_form_data, request=self.request)
            self.assertFalse(person_form.is_valid(), f"PersonRegistrationForm should reject '{weak_password}'")

    def test_minimum_security_requirements_met(self):
        """Test that the implemented solution meets minimum security requirements."""
        # Test that all requirements from the GitHub issue are addressed:
        # 1. Uppercase letter requirement
        with self.assertRaises(ValidationError):
            validate_password("lowercase123!", self.user)

        # 2. Lowercase letter requirement
        with self.assertRaises(ValidationError):
            validate_password("UPPERCASE123!", self.user)

        # 3. Digit requirement
        with self.assertRaises(ValidationError):
            validate_password("NoDigitsHere!", self.user)

        # 4. Special character requirement
        with self.assertRaises(ValidationError):
            validate_password("NoSpecialChars123", self.user)

        # 5. Minimum length requirement (8 characters)
        with self.assertRaises(ValidationError):
            validate_password("Sh0rt!", self.user)

        # 6. Common password rejection
        with self.assertRaises(ValidationError):
            validate_password("password", self.user)

        # Test that a password meeting all requirements is accepted
        strong_password = "SecureP@ssw0rd123"
        try:
            validate_password(strong_password, self.user)
        except ValidationError:
            self.fail(f"Password '{strong_password}' meeting all requirements should be accepted")
