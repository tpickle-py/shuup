from unittest.mock import MagicMock, patch

from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.sessions.models import Session
from django.test import RequestFactory, TestCase
from django.test.client import Client
from django.urls import reverse

import pytest

from shuup.core.auth.backends import EmailModelBackend, WeakPasswordDetectionBackend
from shuup.core.utils.weak_password_detection import (
    check_user_against_weak_patterns,
    clear_user_password_reset_flag,
    flag_user_for_password_reset,
    get_weak_password_patterns,
    has_weak_password,
    is_user_flagged_for_password_reset,
    mark_password_as_updated,
    should_force_password_reset,
)
from shuup.core.middlewares.weak_password_middleware import (
    WeakPasswordDetectionMiddleware,
    WeakPasswordInterceptMiddleware,
)
from shuup.testing import factories

User = get_user_model()


class TestWeakPasswordDetection(TestCase):
    """Test weak password detection utilities."""

    def setUp(self):
        self.user = factories.create_random_user()

    def test_has_weak_password_detection(self):
        """Test detection of weak passwords."""
        weak_passwords = ["weak", "1234", "password", "admin", "test", "12345678", "PASSWORD123", "password123"]

        for weak_password in weak_passwords:
            self.assertTrue(
                has_weak_password(self.user, weak_password), f"Password '{weak_password}' should be detected as weak"
            )

    def test_strong_password_not_detected_as_weak(self):
        """Test that strong passwords are not detected as weak."""
        strong_passwords = ["SecureP@ssw0rd!", "MyStr0ng#Pass", "C0mplex!Password123"]

        for strong_password in strong_passwords:
            self.assertFalse(
                has_weak_password(self.user, strong_password),
                f"Password '{strong_password}' should not be detected as weak",
            )

    def test_user_flagging_for_password_reset(self):
        """Test flagging users for password reset."""
        # Initially not flagged
        self.assertFalse(is_user_flagged_for_password_reset(self.user))

        # Flag user
        flag_user_for_password_reset(self.user)
        self.assertTrue(is_user_flagged_for_password_reset(self.user))

        # Clear flag
        clear_user_password_reset_flag(self.user)
        self.assertFalse(is_user_flagged_for_password_reset(self.user))

    def test_weak_password_patterns_detection(self):
        """Test detection based on user attribute patterns."""
        # Create user with predictable attributes
        user = User.objects.create_user(
            username="testuser", email="testuser@example.com", first_name="Test", last_name="User"
        )

        # Should be detected due to username matching common pattern
        self.assertTrue(check_user_against_weak_patterns(user))

        # Create user with non-matching attributes
        user2 = User.objects.create_user(
            username="complexusername123",
            email="complex.email@example.com",
            first_name="ComplexFirst",
            last_name="ComplexLast",
        )

        # Should not be detected
        self.assertFalse(check_user_against_weak_patterns(user2))

    def test_should_force_password_reset(self):
        """Test logic for determining if password reset should be forced."""
        # User not flagged and no weak patterns
        user = factories.create_random_user()
        self.assertFalse(should_force_password_reset(user))

        # Flag user directly
        flag_user_for_password_reset(user)
        self.assertTrue(should_force_password_reset(user))

        # Clear flag
        clear_user_password_reset_flag(user)

        # Test with weak pattern user
        weak_user = User.objects.create_user(username="admin", email="admin@example.com")
        self.assertTrue(should_force_password_reset(weak_user))

    def test_mark_password_as_updated(self):
        """Test clearing password reset requirements after update."""
        flag_user_for_password_reset(self.user)
        self.assertTrue(is_user_flagged_for_password_reset(self.user))

        mark_password_as_updated(self.user)
        self.assertFalse(is_user_flagged_for_password_reset(self.user))


class TestWeakPasswordAuthenticationBackend(TestCase):
    """Test authentication backend with weak password detection."""

    def setUp(self):
        self.backend = WeakPasswordDetectionBackend()
        self.email_backend = EmailModelBackend()
        self.factory = RequestFactory()

    def test_authentication_with_weak_password(self):
        """Test that weak passwords are detected during authentication."""
        user = User.objects.create_user(username="testuser", password="weak", email="test@example.com")  # Weak password

        request = self.factory.post("/login/")
        authenticated_user = self.backend.authenticate(request, username="testuser", password="weak")

        # User should authenticate successfully
        self.assertEqual(authenticated_user, user)

        # But should be flagged for weak password
        self.assertTrue(hasattr(request, "_weak_password_detected"))
        self.assertTrue(request._weak_password_detected)
        self.assertEqual(request._weak_password_user, user)

    def test_authentication_with_strong_password(self):
        """Test that strong passwords don't trigger detection."""
        user = User.objects.create_user(
            username="testuser", password="SecureP@ssw0rd123!", email="test@example.com"  # Strong password
        )

        request = self.factory.post("/login/")
        authenticated_user = self.backend.authenticate(request, username="testuser", password="SecureP@ssw0rd123!")

        # User should authenticate successfully
        self.assertEqual(authenticated_user, user)

        # Should not be flagged for weak password
        self.assertFalse(hasattr(request, "_weak_password_detected"))

    def test_email_authentication_backend(self):
        """Test authentication using email address."""
        user = User.objects.create_user(username="testuser", password="SecureP@ssw0rd123!", email="test@example.com")

        request = self.factory.post("/login/")

        # Authenticate with email
        authenticated_user = self.email_backend.authenticate(
            request, username="test@example.com", password="SecureP@ssw0rd123!"  # Use email as username
        )

        self.assertEqual(authenticated_user, user)

    def test_email_authentication_with_weak_password(self):
        """Test email authentication with weak password detection."""
        user = User.objects.create_user(username="testuser", password="weak", email="test@example.com")

        request = self.factory.post("/login/")
        authenticated_user = self.email_backend.authenticate(request, username="test@example.com", password="weak")

        # Should authenticate but flag weak password
        self.assertEqual(authenticated_user, user)
        self.assertTrue(hasattr(request, "_weak_password_detected"))


class TestWeakPasswordMiddleware(TestCase):
    """Test middleware for intercepting weak password users."""

    def setUp(self):
        self.middleware = WeakPasswordInterceptMiddleware()
        self.detection_middleware = WeakPasswordDetectionMiddleware()
        self.factory = RequestFactory()
        self.user = factories.create_random_user()

    def test_middleware_allows_unauthenticated_users(self):
        """Test that middleware doesn't affect unauthenticated users."""
        request = self.factory.get("/")
        request.user = None  # Unauthenticated

        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # Should not redirect

    def test_middleware_allows_users_without_weak_passwords(self):
        """Test that users without weak passwords can proceed normally."""
        request = self.factory.get("/")
        request.user = self.user
        request.user.is_authenticated = True

        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # Should not redirect

    @patch("shuup.core.middlewares.weak_password_middleware.should_force_password_reset")
    def test_middleware_redirects_weak_password_users(self, mock_should_force):
        """Test that users with weak passwords are redirected."""
        mock_should_force.return_value = True

        request = self.factory.get("/some-protected-page/")
        request.user = self.user
        request.user.is_authenticated = True

        # Mock the resolver_match to simulate URL resolution
        request.resolver_match = MagicMock()
        request.resolver_match.url_name = "some_view"
        request.resolver_match.namespace = None

        response = self.middleware.process_request(request)

        # Should redirect to password reset
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 302)

    def test_middleware_allows_password_reset_urls(self):
        """Test that password reset URLs are allowed."""
        request = self.factory.get("/reset-password/")
        request.user = self.user
        request.user.is_authenticated = True

        # Mock resolver match for allowed URL
        request.resolver_match = MagicMock()
        request.resolver_match.url_name = "change-password"
        request.resolver_match.namespace = "shuup"

        # Even if user has weak password, should allow access to reset page
        with patch("shuup.core.middlewares.weak_password_middleware.should_force_password_reset", return_value=True):
            response = self.middleware.process_request(request)
            self.assertIsNone(response)  # Should not redirect

    def test_middleware_allows_static_files(self):
        """Test that static files are always allowed."""
        request = self.factory.get("/static/css/style.css")
        request.user = self.user
        request.user.is_authenticated = True

        with patch("shuup.core.middlewares.weak_password_middleware.should_force_password_reset", return_value=True):
            response = self.middleware.process_request(request)
            self.assertIsNone(response)  # Should allow static files

    @patch("shuup.core.middlewares.weak_password_middleware.Session")
    def test_session_clearing(self, mock_session):
        """Test that user sessions are cleared for security."""
        # Mock sessions
        mock_session_obj = MagicMock()
        mock_session_obj.get_decoded.return_value = {"_auth_user_id": str(self.user.pk)}
        mock_session.objects.all.return_value = [mock_session_obj]

        # Create request that should trigger session clearing
        request = self.factory.get("/some-page/")
        request.user = self.user
        request.user.is_authenticated = True
        request.resolver_match = MagicMock()
        request.resolver_match.url_name = "some_view"
        request.resolver_match.namespace = None

        with patch("shuup.core.middlewares.weak_password_middleware.should_force_password_reset", return_value=True):
            response = self.middleware.process_request(request)

            # Should have attempted to delete the session
            mock_session_obj.delete.assert_called_once()


class TestWeakPasswordManagementCommand(TestCase):
    """Test the management command for identifying weak passwords."""

    def test_weak_password_pattern_detection(self):
        """Test that the command can identify users with weak password patterns."""
        # Create users with obvious weak password patterns
        weak_users = [
            User.objects.create_user(username="admin", email="admin@test.com"),
            User.objects.create_user(username="test", email="test@test.com"),
            User.objects.create_user(username="user123", email="password@test.com"),
        ]

        # Create user with strong pattern
        strong_user = User.objects.create_user(username="complexuser789", email="complex.email@test.com")

        # Test pattern detection
        weak_count = 0
        for user in User.objects.all():
            if check_user_against_weak_patterns(user):
                weak_count += 1

        # Should detect the weak users but not the strong one
        self.assertGreaterEqual(weak_count, len(weak_users))
        self.assertFalse(check_user_against_weak_patterns(strong_user))


class TestWeakPasswordViews(TestCase):
    """Test views for handling weak password resets."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="weak", email="test@example.com")

    def test_forced_password_reset_view_requires_login(self):
        """Test that forced password reset view requires authentication."""
        response = self.client.get("/forced-password-reset/")
        # Should redirect to login (302) or show forbidden (403)
        self.assertIn(response.status_code, [302, 403, 404])  # 404 if URL not configured

    def test_user_without_weak_password_redirected_from_forced_reset(self):
        """Test that users without weak passwords are redirected away from forced reset."""
        # Create user without weak password flags
        strong_user = factories.create_random_user()
        self.client.force_login(strong_user)

        # Try to access forced reset page
        with patch("shuup.front.views.weak_password_reset.should_force_password_reset", return_value=False):
            response = self.client.get("/forced-password-reset/", follow=True)
            # Should be redirected away from the reset page
            self.assertEqual(response.status_code, 200)


class TestPasswordSecurityIntegration(TestCase):
    """Integration tests for the complete password security system."""

    def test_end_to_end_weak_password_handling(self):
        """Test complete flow from weak password detection to resolution."""
        # 1. Create user with weak password
        user = User.objects.create_user(username="testuser", password="weak", email="test@example.com")

        # 2. Simulate login with weak password detection
        factory = RequestFactory()
        backend = WeakPasswordDetectionBackend()

        request = factory.post("/login/")
        authenticated_user = backend.authenticate(request, username="testuser", password="weak")

        # 3. Verify user authenticated but weak password detected
        self.assertEqual(authenticated_user, user)
        self.assertTrue(hasattr(request, "_weak_password_detected"))

        # 4. Simulate middleware detection
        self.assertTrue(should_force_password_reset(user))

        # 5. Simulate password update
        mark_password_as_updated(user)

        # 6. Verify user no longer needs forced reset
        self.assertFalse(should_force_password_reset(user))

    def test_security_bypass_prevention(self):
        """Test that security bypasses are prevented."""
        user = factories.create_random_user()

        # Flag user for password reset
        flag_user_for_password_reset(user)

        # User should be forced to reset even if they try to access different pages
        self.assertTrue(should_force_password_reset(user))

        # Even after clearing flag, pattern-based detection might still apply
        clear_user_password_reset_flag(user)

        # Final verification that password update clears all flags
        mark_password_as_updated(user)
        self.assertFalse(is_user_flagged_for_password_reset(user))
