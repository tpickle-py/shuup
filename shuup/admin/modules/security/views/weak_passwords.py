"""
Weak password user management views.
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView

from shuup.admin.utils.picotable import Column
from shuup.admin.utils.views import PicotableListView
from shuup.core.utils.weak_password_detection import (
    check_user_against_weak_patterns,
    flag_user_for_password_reset,
    get_weak_password_patterns,
)

from ..forms import BulkSecurityActionForm


@method_decorator(staff_member_required, name="dispatch")
class WeakPasswordListView(PicotableListView):
    """
    List view for users with potentially weak passwords.
    Only accessible to admin staff.
    """

    def dispatch(self, request, *args, **kwargs):
        """Ensure only staff with proper permissions can access."""
        # TODO : Need to make sure this is only accessible to staff with security permissions, not just any staff, additional check needed.
        user = request.user
        if user.is_anonymous:
            messages.error(request, _("You must be logged in to access this page."))
            return redirect("shuup_admin:login")
        if user.is_authenticated and not user.is_active:
            messages.error(request, _("Your account is inactive. Please contact support."))
            return redirect("shuup_admin:login")
        is_staff = getattr(user, "is_staff", False)
        if not is_staff:
            # TODO: Probable should log this attempt and possible alert admins, maybe even block the user
            messages.error(request, _("Access denied. Admin privileges required."))
            return redirect("shuup_admin:dashboard")

        return super().dispatch(request, *args, **kwargs)

    template_name = "shuup/admin/security/weak_password_list.html"
    user_model = get_user_model()
    default_columns = [
        Column(
            "username",
            _("Username"),
            sort_field="username",
        ),
        Column(
            "email",
            _("Email"),
            sort_field="email",
        ),
        Column(
            "first_name",
            _("First Name"),
            sort_field="first_name",
        ),
        Column(
            "last_name",
            _("Last Name"),
            sort_field="last_name",
        ),
        Column(
            "is_staff",
            _("Staff"),
            display="is_staff_display",
        ),
        Column(
            "last_login",
            _("Last Login"),
            sort_field="last_login",
        ),
        Column(
            "matched_patterns",
            _("Risk Patterns"),
            display="get_matched_patterns",
        ),
        Column(
            "actions",
            _("Actions"),
            display="get_actions_html",
        ),
    ]

    def get_queryset(self):
        """Filter to only show users with potentially weak passwords."""
        user_model = get_user_model()
        weak_password_users = []

        for user in user_model.objects.filter(is_active=True):
            if check_user_against_weak_patterns(user):
                # Add matched patterns as a property for display
                # TODO: Add a property to the user model instead of this
                user.matched_patterns = self._get_user_matched_patterns(user)

                weak_password_users.append(user)

        return weak_password_users

    def _get_user_matched_patterns(self, user):
        """Get patterns that match for this user."""
        username = getattr(user, "username", "").lower()
        email = getattr(user, "email", "").lower().split("@")[0]
        first_name = getattr(user, "first_name", "").lower()
        last_name = getattr(user, "last_name", "").lower()

        user_attributes = [attr for attr in [username, email, first_name, last_name] if attr]
        matched_patterns = []

        for pattern in get_weak_password_patterns():
            if any(pattern in attr or attr in pattern for attr in user_attributes):
                matched_patterns.append(pattern)

        return matched_patterns

    def is_staff_display(self, instance):
        """Display staff status with styling."""
        if getattr(instance, "is_staff", False):
            return '<span class="badge badge-warning">Staff</span>'
        return '<span class="badge badge-secondary">Customer</span>'

    def get_matched_patterns(self, instance):
        """Display matched patterns."""
        patterns = getattr(instance, "matched_patterns", [])
        if patterns:
            pattern_badges = [f'<span class="badge badge-danger">{pattern}</span>' for pattern in patterns[:3]]
            if len(patterns) > 3:
                pattern_badges.append(f'<span class="badge badge-light">+{len(patterns) - 3} more</span>')
            return " ".join(pattern_badges)
        return '<span class="text-muted">Heuristic match</span>'

    def get_actions_html(self, instance):
        """Generate action buttons for each user."""
        actions = []

        # View details
        actions.append(
            f'<a href="{reverse("shuup_admin:security.weak_password_detail", kwargs={"pk": instance.pk})}" '
            f'class="btn btn-sm btn-info" title="{_("View Details")}">'
            f'<i class="fa fa-eye"></i></a>'
        )

        # Send notification
        actions.append(
            f'<button class="btn btn-sm btn-warning send-notification" '
            f'data-user-id="{instance.pk}" title="{_("Send Notification")}">'
            f'<i class="fa fa-envelope"></i></button>'
        )

        # Flag for reset
        actions.append(
            f'<button class="btn btn-sm btn-danger flag-reset" '
            f'data-user-id="{instance.pk}" title="{_("Flag for Reset")}">'
            f'<i class="fa fa-flag"></i></button>'
        )

        return " ".join(actions)


@method_decorator(staff_member_required, name="dispatch")
class WeakPasswordDetailView(DetailView):
    """
    Detail view for a specific user with weak password.
    Only accessible to admin staff.
    """

    def dispatch(self, request, *args, **kwargs):
        """Ensure only staff with proper permissions can access."""
        if not request.user.is_staff:
            messages.error(request, _("Access denied. Admin privileges required."))
            return redirect("shuup_admin:dashboard")

        return super().dispatch(request, *args, **kwargs)

    template_name = "shuup/admin/security/weak_password_detail.html"
    model = get_user_model()
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        # Get matched patterns
        username = getattr(user, "username", "").lower()
        email = getattr(user, "email", "").lower().split("@")[0]
        first_name = getattr(user, "first_name", "").lower()
        last_name = getattr(user, "last_name", "").lower()

        user_attributes = [attr for attr in [username, email, first_name, last_name] if attr]
        matched_patterns = []

        for pattern in get_weak_password_patterns():
            if any(pattern in attr or attr in pattern for attr in user_attributes):
                matched_patterns.append(pattern)

        context.update(
            {
                "title": _("Security Risk Details: %s") % user.username,
                "matched_patterns": matched_patterns,
                "user_attributes": {
                    "username": username,
                    "email_prefix": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
                "security_recommendations": self._get_security_recommendations(user),
            }
        )

        return context

    def _get_security_recommendations(self, user):
        """Get specific security recommendations for this user."""
        recommendations = []

        if getattr(user, "is_staff", False):
            recommendations.append(
                {
                    "level": "critical",
                    "title": _("Administrator Account"),
                    "description": _(
                        "This is an administrative account. Password security is critical for system protection."
                    ),
                    "action": _("Immediate password reset required"),
                }
            )

        if not user.last_login:
            recommendations.append(
                {
                    "level": "warning",
                    "title": _("Never Logged In"),
                    "description": _("User has never logged in. Consider account verification."),
                    "action": _("Verify account status and send welcome email"),
                }
            )

        recommendations.append(
            {
                "level": "info",
                "title": _("Password Policy Enforcement"),
                "description": _("Ensure new password meets current security requirements."),
                "action": _("Force password reset with validation"),
            }
        )

        return recommendations

    def post(self, request, *args, **kwargs):
        """Handle actions on user detail page."""
        self.object = self.get_object()
        action = request.POST.get("action")

        if action == "send_notification":
            return self._send_notification()
        elif action == "flag_reset":
            return self._flag_for_reset()
        elif action == "send_reset_email":
            return self._send_reset_email()

        messages.error(request, _("Invalid action."))
        return HttpResponseRedirect(request.get_full_path())

    def _send_notification(self):
        """Send weak password notification to user."""
        try:
            context = {
                "user": self.object,
                "site_name": getattr(settings, "SITE_NAME", "Our Website"),
                "site_url": getattr(settings, "SITE_URL", "https://yoursite.com"),
                "is_staff": getattr(self.object, "is_staff", False),
            }

            subject = render_to_string("shuup/emails/weak_password_notification_subject.txt", context).strip()
            message = render_to_string("shuup/emails/weak_password_notification.txt", context)
            html_message = render_to_string("shuup/emails/weak_password_notification.html", context)

            send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.object.email],
                fail_silently=False,
            )

            messages.success(self.request, _("Notification sent successfully to %s.") % self.object.email)

        except Exception as e:
            messages.error(self.request, _("Failed to send notification: %s") % str(e))

        return HttpResponseRedirect(self.request.get_full_path())

    def _flag_for_reset(self):
        """Flag user for mandatory password reset."""
        flag_user_for_password_reset(self.object)
        messages.success(self.request, _("User %s flagged for mandatory password reset.") % self.object.username)
        return HttpResponseRedirect(self.request.get_full_path())

    def _send_reset_email(self):
        """Send password reset email."""
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        try:
            # Generate reset token
            token = default_token_generator.make_token(self.object)
            uid = urlsafe_base64_encode(force_bytes(self.object.pk))

            context = {
                "user": self.object,
                "site_name": getattr(settings, "SITE_NAME", "Our Website"),
                "site_url": getattr(settings, "SITE_URL", "https://yoursite.com"),
                "uid": uid,
                "token": token,
                "protocol": "https",
                "domain": getattr(settings, "ALLOWED_HOSTS", ["localhost"])[0],
            }

            subject = render_to_string("shuup/emails/password_reset_subject.txt", context).strip()
            message = render_to_string("shuup/emails/password_reset_email.txt", context)
            html_message = render_to_string("shuup/emails/password_reset_email.html", context)

            send_mail(
                subject=subject,
                message=message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.object.email],
                fail_silently=False,
            )

            messages.success(self.request, _("Password reset email sent to %s.") % self.object.email)

        except Exception as e:
            messages.error(self.request, _("Failed to send password reset email: %s") % str(e))

        return HttpResponseRedirect(self.request.get_full_path())


@method_decorator(staff_member_required, name="dispatch")
class BulkSecurityActionView(FormView):
    """
    View for performing bulk security actions on multiple users.
    Only accessible to admin staff.
    """

    def dispatch(self, request, *args, **kwargs):
        """Ensure only staff with proper permissions can access."""
        if not request.user.is_staff:
            messages.error(request, _("Access denied. Admin privileges required."))
            return redirect("shuup_admin:dashboard")

        return super().dispatch(request, *args, **kwargs)

    template_name = "shuup/admin/security/bulk_actions.html"
    form_class = BulkSecurityActionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": _("Bulk Security Actions"),
            }
        )
        return context

    def form_valid(self, form):
        """Process bulk security actions."""
        action = form.cleaned_data["action"]
        user_ids = form.cleaned_data["user_ids"]

        User = get_user_model()
        users = User.objects.filter(id__in=user_ids, is_active=True)

        if action == "send_notifications":
            return self._send_bulk_notifications(users)
        elif action == "flag_for_reset":
            return self._flag_bulk_for_reset(users)
        elif action == "send_reset_emails":
            return self._send_bulk_reset_emails(users)
        elif action == "deactivate_accounts":
            return self._deactivate_bulk_accounts(users)

        messages.error(self.request, _("Invalid action selected."))
        return self.form_invalid(form)

    def _send_bulk_notifications(self, users):
        """Send notifications to multiple users."""
        sent_count = 0
        failed_count = 0

        for user in users:
            try:
                context = {
                    "user": user,
                    "site_name": getattr(settings, "SITE_NAME", "Our Website"),
                    "site_url": getattr(settings, "SITE_URL", "https://yoursite.com"),
                    "is_staff": getattr(user, "is_staff", False),
                }

                subject = render_to_string("shuup/emails/weak_password_notification_subject.txt", context).strip()
                message = render_to_string("shuup/emails/weak_password_notification.txt", context)
                html_message = render_to_string("shuup/emails/weak_password_notification.html", context)

                send_mail(
                    subject=subject,
                    message=message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                sent_count += 1

            except Exception:
                failed_count += 1

        if sent_count > 0:
            messages.success(self.request, _("Notifications sent to %d users.") % sent_count)
        if failed_count > 0:
            messages.warning(self.request, _("Failed to send notifications to %d users.") % failed_count)

        return HttpResponseRedirect(reverse("shuup_admin:security.weak_passwords"))

    def _flag_bulk_for_reset(self, users):
        """Flag multiple users for password reset."""
        count = 0
        for user in users:
            flag_user_for_password_reset(user)
            count += 1

        messages.success(self.request, _("Flagged %d users for mandatory password reset.") % count)
        return HttpResponseRedirect(reverse("shuup_admin:security.weak_passwords"))

    def _send_bulk_reset_emails(self, users):
        """Send password reset emails to multiple users."""
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        sent_count = 0
        failed_count = 0

        for user in users:
            try:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                context = {
                    "user": user,
                    "site_name": getattr(settings, "SITE_NAME", "Our Website"),
                    "site_url": getattr(settings, "SITE_URL", "https://yoursite.com"),
                    "uid": uid,
                    "token": token,
                    "protocol": "https",
                    "domain": getattr(settings, "ALLOWED_HOSTS", ["localhost"])[0],
                }

                subject = render_to_string("shuup/emails/password_reset_subject.txt", context).strip()
                message = render_to_string("shuup/emails/password_reset_email.txt", context)
                html_message = render_to_string("shuup/emails/password_reset_email.html", context)

                send_mail(
                    subject=subject,
                    message=message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                sent_count += 1

            except Exception:
                failed_count += 1

        if sent_count > 0:
            messages.success(self.request, _("Password reset emails sent to %d users.") % sent_count)
        if failed_count > 0:
            messages.warning(self.request, _("Failed to send reset emails to %d users.") % failed_count)

        return HttpResponseRedirect(reverse("shuup_admin:security.weak_passwords"))

    def _deactivate_bulk_accounts(self, users):
        """Deactivate multiple user accounts."""
        count = users.update(is_active=False)
        messages.warning(self.request, _("Deactivated %d user accounts.") % count)
        return HttpResponseRedirect(reverse("shuup_admin:security.weak_passwords"))
