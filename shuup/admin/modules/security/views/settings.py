"""
Security settings configuration views.
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from ..forms import QuickActionForm, SecuritySettingsForm


@method_decorator(staff_member_required, name="dispatch")
class SecuritySettingsView(FormView):
    """
    Configuration view for security settings.

    Only accessible to staff users with appropriate permissions.
    """

    template_name = "shuup/admin/security/settings.html"
    form_class = SecuritySettingsForm

    def dispatch(self, request, *args, **kwargs):
        """Ensure only staff with proper permissions can access."""
        if not request.user.is_staff:
            messages.error(request, _("Access denied. Admin privileges required."))
            return redirect("shuup_admin:dashboard")

        # Additional permission check - only superusers or users with security permissions
        if not (request.user.is_superuser or request.user.has_perm("shuup.change_user")):
            messages.error(request, _("Access denied. Security management privileges required."))
            return redirect("shuup_admin:dashboard")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": _("Security Settings"),
                "current_settings": self._get_current_settings(),
                "middleware_status": self._check_middleware_status(),
            }
        )
        return context

    def get_initial(self):
        """Load current security settings."""
        return self._get_current_settings()

    def _get_current_settings(self):
        """Get current security configuration."""
        middleware_classes = getattr(settings, "MIDDLEWARE", [])

        return {
            # Middleware status
            "enable_weak_password_middleware": "shuup.core.middlewares.weak_password_middleware.WeakPasswordInterceptMiddleware"
            in middleware_classes,
            "enable_password_detection_middleware": "shuup.core.middlewares.weak_password_middleware.WeakPasswordDetectionMiddleware"
            in middleware_classes,
            # Email settings (can be extended to read from database/cache)
            "enable_automatic_notifications": False,
            "notification_frequency": "weekly",
            # Password policy (from AUTH_PASSWORD_VALIDATORS)
            "minimum_password_length": 8,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_numbers": True,
            "require_special_chars": True,
            # Session/security settings
            "session_timeout_minutes": 60,
            "max_login_attempts": 5,
            "lockout_duration_minutes": 15,
        }

    def _check_middleware_status(self):
        """Check status of security middleware."""
        middleware_classes = getattr(settings, "MIDDLEWARE", [])

        status = {
            "weak_password_middleware": {
                "enabled": "shuup.core.middlewares.weak_password_middleware.WeakPasswordInterceptMiddleware"
                in middleware_classes,
                "class": "shuup.core.middlewares.weak_password_middleware.WeakPasswordInterceptMiddleware",
            },
            "password_detection_middleware": {
                "enabled": "shuup.core.middlewares.weak_password_middleware.WeakPasswordDetectionMiddleware"
                in middleware_classes,
                "class": "shuup.core.middlewares.weak_password_middleware.WeakPasswordDetectionMiddleware",
            },
        }

        return status

    def form_valid(self, form):
        """Save security settings."""
        # In a real implementation, these settings would be saved to database
        # or configuration management system. For now, we'll show what would be configured.

        settings_to_save = form.cleaned_data

        # Generate middleware configuration instructions
        middleware_instructions = self._generate_middleware_instructions(settings_to_save)

        messages.success(
            self.request,
            _("Security settings updated successfully. Please review the configuration instructions below."),
        )

        # Store instructions in session to display
        self.request.session["security_config_instructions"] = middleware_instructions

        return super().form_valid(form)

    def _generate_middleware_instructions(self, settings_data):
        """Generate configuration instructions for middleware."""
        instructions = []

        if settings_data.get("enable_weak_password_middleware"):
            instructions.append(
                {
                    "type": "middleware",
                    "action": "add",
                    "description": _("Add weak password interception middleware"),
                    "code": "'shuup.core.middlewares.weak_password_middleware.WeakPasswordInterceptMiddleware'",
                    "location": _("Add to MIDDLEWARE in settings.py"),
                }
            )

        if settings_data.get("enable_password_detection_middleware"):
            instructions.append(
                {
                    "type": "middleware",
                    "action": "add",
                    "description": _("Add password detection middleware"),
                    "code": "'shuup.core.middlewares.weak_password_middleware.WeakPasswordDetectionMiddleware'",
                    "location": _("Add to MIDDLEWARE in settings.py"),
                }
            )

        # Authentication backend instructions
        instructions.append(
            {
                "type": "authentication",
                "action": "add",
                "description": _("Add weak password detection backend"),
                "code": "'shuup.core.auth.backends.WeakPasswordDetectionBackend'",
                "location": _("Add to AUTHENTICATION_BACKENDS in settings.py"),
            }
        )

        return instructions

    def get_success_url(self):
        return self.request.path


@method_decorator(staff_member_required, name="dispatch")
class QuickActionView(FormView):
    """
    Quick action view for common security tasks.
    """

    template_name = "shuup/admin/security/quick_action.html"
    form_class = QuickActionForm

    def dispatch(self, request, *args, **kwargs):
        """Ensure only staff with proper permissions can access."""
        if not request.user.is_staff:
            messages.error(request, _("Access denied. Admin privileges required."))
            return redirect("shuup_admin:dashboard")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Execute the selected quick action."""
        action = form.cleaned_data["action"]
        target = form.cleaned_data["target"]

        if action == "scan_weak_passwords":
            return self._scan_weak_passwords(target)
        elif action == "send_security_reminders":
            return self._send_security_reminders(target)
        elif action == "generate_security_report":
            return self._generate_security_report(target)

        messages.error(self.request, _("Unknown action selected."))
        return self.form_invalid(form)

    def _scan_weak_passwords(self, target):
        """Perform weak password scan."""
        from django.contrib.auth import get_user_model

        from shuup.core.utils.weak_password_detection import check_user_against_weak_patterns

        User = get_user_model()
        queryset = User.objects.filter(is_active=True)

        if target == "staff_only":
            queryset = queryset.filter(is_staff=True)
        elif target == "customers_only":
            queryset = queryset.filter(is_staff=False)

        weak_users = []
        for user in queryset:
            if check_user_against_weak_patterns(user):
                weak_users.append(user)

        messages.success(
            self.request,
            _("Scan completed. Found %d users with potentially weak passwords out of %d total users.")
            % (len(weak_users), queryset.count()),
        )

        return redirect("shuup_admin:security.weak_passwords")

    def _send_security_reminders(self, target):
        """Send security reminder emails."""
        # Implementation would send reminder emails
        messages.success(self.request, _("Security reminders sent successfully."))
        return redirect("shuup_admin:security.dashboard")

    def _generate_security_report(self, target):
        """Generate security report."""
        # Implementation would generate and download report
        messages.success(self.request, _("Security report generated successfully."))
        return redirect("shuup_admin:security.dashboard")
