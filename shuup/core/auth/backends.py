"""
Custom authentication backends for Shuup.

This module provides authentication backends that enhance security
by detecting weak passwords during the login process.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from shuup.core.utils.weak_password_detection import flag_user_for_password_reset, has_weak_password


class WeakPasswordDetectionBackend(ModelBackend):
    """
    Authentication backend that detects weak passwords during login.

    This backend extends Django's default ModelBackend to detect when
    users authenticate with weak passwords and flag them for forced reset.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user and detect weak passwords.

        Args:
            request: Django request object
            username: Username or email
            password: Plain text password
            **kwargs: Additional authentication parameters

        Returns:
            User instance if authentication successful, None otherwise
        """
        # First, try normal authentication
        user = super().authenticate(request, username, password, **kwargs)

        if user is not None and password:
            # User authenticated successfully, now check password strength
            if has_weak_password(user, password):
                # Flag user for password reset
                flag_user_for_password_reset(user)

                # Set a flag on the request for the middleware to pick up
                if request:
                    request._weak_password_detected = True
                    request._weak_password_user = user

        return user


class EmailModelBackend(WeakPasswordDetectionBackend):
    """
    Authentication backend that allows login with email address.

    This backend extends WeakPasswordDetectionBackend to support
    authentication with email addresses instead of just usernames.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate using email or username.

        Args:
            request: Django request object
            username: Username or email address
            password: Plain text password
            **kwargs: Additional authentication parameters

        Returns:
            User instance if authentication successful, None otherwise
        """
        UserModel = get_user_model()

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if username is None or password is None:
            return None

        # Try to find user by username first
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # If not found by username, try by email
            try:
                user = UserModel._default_manager.get(email=username)
            except UserModel.DoesNotExist:
                # Run the default password hasher once to reduce the timing
                # difference between an existing and a nonexistent user (#20760).
                UserModel().set_password(password)
                return None

        # Check password and detect weak passwords
        if user.check_password(password) and self.user_can_authenticate(user):
            # Check for weak password
            if has_weak_password(user, password):
                flag_user_for_password_reset(user)
                if request:
                    request._weak_password_detected = True
                    request._weak_password_user = user

            return user

        return None
