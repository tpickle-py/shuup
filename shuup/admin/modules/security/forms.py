"""
Forms for security administration.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class BulkSecurityActionForm(forms.Form):
    """
    Form for performing bulk security actions.
    """

    ACTION_CHOICES = [
        ("send_notifications", _("Send weak password notifications")),
        ("flag_for_reset", _("Flag for mandatory password reset")),
        ("send_reset_emails", _("Send password reset emails")),
        ("deactivate_accounts", _("Deactivate accounts (CAUTION)")),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES, label=_("Action"), help_text=_("Select the action to perform on selected users.")
    )

    user_ids = forms.CharField(widget=forms.HiddenInput(), help_text=_("Comma-separated list of user IDs"))

    confirm_action = forms.BooleanField(
        required=True,
        label=_("I understand the consequences of this action"),
        help_text=_("Please confirm you understand this action affects multiple users."),
    )

    def clean_user_ids(self):
        """Validate and convert user IDs."""
        user_ids_str = self.cleaned_data.get("user_ids", "")

        if not user_ids_str.strip():
            raise forms.ValidationError(_("No users selected."))

        try:
            user_ids = [int(uid.strip()) for uid in user_ids_str.split(",") if uid.strip()]
        except ValueError as exc:
            raise forms.ValidationError(_("Invalid user ID format.")) from exc

        if not user_ids:
            raise forms.ValidationError(_("No valid user IDs provided."))

        # Verify users exist
        users = get_user_model()
        existing_count = users.objects.filter(id__in=user_ids, is_active=True).count()

        if existing_count != len(user_ids):
            raise forms.ValidationError(_("Some users no longer exist or are inactive. Please refresh the list."))

        return user_ids


class SecuritySettingsForm(forms.Form):
    """
    Form for configuring security settings.
    """

    # Middleware settings
    enable_weak_password_middleware = forms.BooleanField(
        required=False,
        label=_("Enable weak password interception"),
        help_text=_("Intercept users with weak passwords and force password reset."),
    )

    enable_password_detection_middleware = forms.BooleanField(
        required=False,
        label=_("Enable password detection during login"),
        help_text=_("Detect weak passwords when users log in."),
    )

    # Email notification settings
    enable_automatic_notifications = forms.BooleanField(
        required=False,
        label=_("Enable automatic notifications"),
        help_text=_("Automatically send notifications to users with weak passwords."),
    )

    notification_frequency = forms.ChoiceField(
        choices=[
            ("daily", _("Daily")),
            ("weekly", _("Weekly")),
            ("monthly", _("Monthly")),
        ],
        initial="weekly",
        label=_("Notification frequency"),
        help_text=_("How often to send notifications to users with weak passwords."),
    )

    # Security policy settings
    minimum_password_length = forms.IntegerField(
        min_value=6,
        max_value=32,
        initial=8,
        label=_("Minimum password length"),
        help_text=_("Minimum number of characters required for passwords."),
    )

    require_uppercase = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Require uppercase letters"),
        help_text=_("Passwords must contain at least one uppercase letter."),
    )

    require_lowercase = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Require lowercase letters"),
        help_text=_("Passwords must contain at least one lowercase letter."),
    )

    require_numbers = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Require numbers"),
        help_text=_("Passwords must contain at least one number."),
    )

    require_special_chars = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Require special characters"),
        help_text=_("Passwords must contain at least one special character."),
    )

    # Additional security options
    session_timeout_minutes = forms.IntegerField(
        min_value=5,
        max_value=1440,  # 24 hours
        initial=60,
        label=_("Session timeout (minutes)"),
        help_text=_("Automatically log out inactive users after this time."),
    )

    max_login_attempts = forms.IntegerField(
        min_value=3,
        max_value=10,
        initial=5,
        label=_("Maximum login attempts"),
        help_text=_("Number of failed login attempts before temporary lockout."),
    )

    lockout_duration_minutes = forms.IntegerField(
        min_value=5,
        max_value=60,
        initial=15,
        label=_("Lockout duration (minutes)"),
        help_text=_("How long to lock accounts after failed login attempts."),
    )


class QuickActionForm(forms.Form):
    """
    Form for quick security actions from the dashboard.
    """

    action = forms.ChoiceField(
        choices=[
            ("scan_weak_passwords", _("Scan for weak passwords")),
            ("send_security_reminders", _("Send security reminders")),
            ("generate_security_report", _("Generate security report")),
        ],
        label=_("Quick Action"),
    )

    target = forms.ChoiceField(
        choices=[
            ("all_users", _("All users")),
            ("staff_only", _("Staff users only")),
            ("customers_only", _("Customers only")),
        ],
        initial="all_users",
        label=_("Target users"),
    )


class UserSecurityForm(forms.Form):
    """
    Form for individual user security actions.
    """

    action = forms.ChoiceField(
        choices=[
            ("send_notification", _("Send weak password notification")),
            ("send_reset_email", _("Send password reset email")),
            ("flag_for_reset", _("Flag for mandatory password reset")),
            ("clear_reset_flag", _("Clear password reset flag")),
        ],
        label=_("Action"),
    )

    include_security_tips = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Include security tips"),
        help_text=_("Include password security recommendations in notifications."),
    )

    custom_message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False,
        label=_("Custom message"),
        help_text=_("Optional custom message to include in notifications."),
    )
