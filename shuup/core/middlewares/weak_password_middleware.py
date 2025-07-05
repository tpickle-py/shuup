"""
Middleware to handle users with weak passwords.

This middleware intercepts requests from authenticated users who have weak passwords
and redirects them to a forced password reset page.
"""

# Import Session model inside methods to avoid Django setup issues
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils.translation import gettext_lazy as _

from shuup.core.utils.weak_password_detection import should_force_password_reset


class WeakPasswordInterceptMiddleware(MiddlewareMixin):
    """
    Middleware that intercepts users with weak passwords and forces password reset.

    This middleware:
    1. Checks if authenticated users have weak passwords
    2. Redirects them to forced password reset
    3. Clears sessions to prevent bypasses
    4. Excludes the password reset URLs to prevent redirect loops
    """

    # URLs that should be accessible during forced password reset
    ALLOWED_URLS = [
        "shuup_admin:user.reset-password",
        "shuup_admin:user.change-password",
        "shuup:customer_information.change_password",
        "shuup_admin:login",
        "shuup:auth.logout",
        "shuup:auth.login",
        "weak_password_reset",  # Our custom forced reset URL
    ]

    # URL patterns that should be accessible (for static files, etc.)
    ALLOWED_PATTERNS = [
        "/static/",
        "/media/",
        "/api/weak-password-check/",  # For AJAX checks
    ]

    def process_request(self, request):
        """
        Process the request and check for weak password users.

        Args:
            request: Django request object

        Returns:
            HttpResponseRedirect if user needs password reset, None otherwise
        """
        # Skip if user is not authenticated
        if not request.user.is_authenticated:
            return None

        # Skip if we're already on an allowed URL
        if self._is_url_allowed(request):
            return None

        # Check if user should be forced to reset password
        if should_force_password_reset(request.user):
            return self._handle_weak_password_user(request)

        return None

    def _is_url_allowed(self, request):
        """
        Check if the current URL should be allowed during forced password reset.

        Args:
            request: Django request object

        Returns:
            bool: True if URL is allowed
        """
        path = request.path

        # Check allowed URL patterns
        for pattern in self.ALLOWED_PATTERNS:
            if path.startswith(pattern):
                return True

        # Check allowed URL names
        if hasattr(request, "resolver_match") and request.resolver_match:
            url_name = request.resolver_match.url_name
            namespace = request.resolver_match.namespace

            # Build full URL name with namespace
            full_url_name = f"{namespace}:{url_name}" if namespace else url_name

            if full_url_name in self.ALLOWED_URLS or url_name in self.ALLOWED_URLS:
                return True

        return False

    def _handle_weak_password_user(self, request):
        """
        Handle a user with a weak password.

        Args:
            request: Django request object

        Returns:
            HttpResponseRedirect to password reset page
        """
        # Clear all user sessions for security
        self._clear_user_sessions(request.user)

        # Add warning message
        messages.warning(
            request,
            _(
                "For your security, you must update your password. "
                "Your current password does not meet our security requirements."
            ),
        )

        # Determine appropriate password reset URL based on user type
        if getattr(request.user, "is_staff", False):
            # Admin user - redirect to admin password change
            try:
                reset_url = reverse("shuup_admin:user.change-password", kwargs={"pk": request.user.pk})
            except:  # noqa: E722
                reset_url = reverse("shuup_admin:login")
        else:
            # Regular user - redirect to customer password change
            try:
                reset_url = reverse("shuup:customer_information.change_password")
            except:  # noqa: E722
                reset_url = reverse("shuup:auth.login")

        return HttpResponseRedirect(reset_url)

    def _clear_user_sessions(self, user):
        """
        Clear all active sessions for a user to prevent bypass attempts.

        Args:
            user: User instance
        """
        try:
            # Import Session model here to avoid Django setup issues
            from django.contrib.sessions.models import Session

            # Get all sessions and clear those belonging to this user
            sessions = Session.objects.all()

            for session in sessions:
                session_data = session.get_decoded()
                if session_data.get("_auth_user_id") == str(user.pk):
                    session.delete()

        except Exception:
            # If we can't clear sessions, log the issue but don't break the flow
            # In production, you'd want proper logging here
            pass


class WeakPasswordDetectionMiddleware(MiddlewareMixin):
    """
    Middleware to detect weak passwords during login.

    This middleware works with Django's authentication system to check
    passwords during the login process.
    """

    def process_request(self, request):
        """
        Check for weak password detection during login.

        This middleware hooks into the login process to detect when
        a user successfully authenticates with a weak password.
        """
        # This middleware works in conjunction with a custom authentication backend
        # or signal handlers that can detect weak passwords during login

        # Check if we have a flag indicating a weak password was just detected
        if hasattr(request, "_weak_password_detected"):
            user = getattr(request, "user", None)
            if user and user.is_authenticated:
                from shuup.core.utils.weak_password_detection import flag_user_for_password_reset

                flag_user_for_password_reset(user)

        return None
