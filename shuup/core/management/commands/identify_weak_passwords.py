"""
Management command to identify users with potentially weak passwords.

This command helps administrators identify users who may have weak passwords
that need to be updated for security compliance.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from shuup.core.utils.weak_password_detection import check_user_against_weak_patterns, get_weak_password_patterns


class Command(BaseCommand):
    help = "Identify users who may have weak passwords based on heuristic analysis"

    def add_arguments(self, parser):
        parser.add_argument("--export-csv", type=str, help="Export results to CSV file")
        parser.add_argument(
            "--email-notify",
            action="store_true",
            help="Send email notifications to users with potentially weak passwords",
        )
        parser.add_argument(
            "--email-reset", action="store_true", help="Send password reset emails to users with weak passwords"
        )
        parser.add_argument(
            "--email-security-breach", action="store_true", help="Send security breach notification emails"
        )
        parser.add_argument(
            "--deactivate-accounts",
            action="store_true",
            help="Deactivate accounts with weak passwords (use with extreme caution)",
        )
        parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
        parser.add_argument("--staff-only", action="store_true", help="Only check staff users")
        parser.add_argument("--exclude-staff", action="store_true", help="Exclude staff users from check")
        parser.add_argument(
            "--force-email",
            action="store_true",
            help="Force sending emails even if email backend is not properly configured (for testing)",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        # Build query based on options
        queryset = User.objects.filter(is_active=True)

        if options["staff_only"]:
            queryset = queryset.filter(is_staff=True)
        elif options["exclude_staff"]:
            queryset = queryset.filter(is_staff=False)

        self.stdout.write("🔍 Analyzing users for potential weak passwords...")
        self.stdout.write(f"Total users to check: {queryset.count()}")

        weak_password_users = []
        patterns_found = {}

        for user in queryset:
            if check_user_against_weak_patterns(user):
                weak_password_users.append(user)

                # Track which patterns were matched
                username = getattr(user, "username", "").lower()
                email = getattr(user, "email", "").lower().split("@")[0]
                first_name = getattr(user, "first_name", "").lower()
                last_name = getattr(user, "last_name", "").lower()

                user_attributes = [attr for attr in [username, email, first_name, last_name] if attr]
                matched_patterns = []

                for pattern in get_weak_password_patterns():
                    if any(pattern in attr or attr in pattern for attr in user_attributes):
                        matched_patterns.append(pattern)

                patterns_found[user.pk] = matched_patterns

        # Report results
        self.stdout.write("\n📊 Analysis Results:")
        self.stdout.write(f"Users with potentially weak passwords: {len(weak_password_users)}")
        self.stdout.write(f"Percentage of users at risk: {len(weak_password_users)/queryset.count()*100:.1f}%")

        if weak_password_users:
            self.stdout.write("\n⚠️  Users requiring attention:")
            for user in weak_password_users:
                user_type = "Staff" if getattr(user, "is_staff", False) else "Customer"
                patterns = patterns_found.get(user.pk, [])

                self.stdout.write(
                    f"  - {user.username} ({user.email}) [{user_type}] "
                    f"- Patterns: {', '.join(patterns) if patterns else 'General heuristic match'}"
                )

        # Check email configuration before any email operations
        email_configured = self._check_email_configuration(options.get("force_email", False))

        # Export to CSV if requested
        if options["export_csv"] and weak_password_users:
            self._export_to_csv(weak_password_users, patterns_found, options["export_csv"])

        # Handle account deactivation if requested
        if options["deactivate_accounts"] and weak_password_users:
            self._handle_account_deactivation(weak_password_users, options["dry_run"])

        # Send various types of email notifications if requested
        if weak_password_users and email_configured and not options["dry_run"]:
            if options["email_notify"]:
                self._send_weak_password_notifications(weak_password_users)

            if options["email_reset"]:
                self._send_password_reset_emails(weak_password_users)

            if options["email_security_breach"]:
                self._send_security_breach_notifications(weak_password_users)

        elif (
            options["email_notify"] or options["email_reset"] or options["email_security_breach"]
        ) and not email_configured:
            self.stdout.write("❌ Email notifications skipped - email not properly configured")
            self.stdout.write("   Configure EMAIL_BACKEND and related settings, or use --force-email for testing")

        # Show recommendations
        self._show_recommendations(len(weak_password_users), queryset.count())

    def _export_to_csv(self, users, patterns_found, filename):
        """Export weak password users to CSV file."""
        import csv

        try:
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [
                        "Username",
                        "Email",
                        "First Name",
                        "Last Name",
                        "Is Staff",
                        "Date Joined",
                        "Last Login",
                        "Matched Patterns",
                    ]
                )

                for user in users:
                    patterns = patterns_found.get(user.pk, [])
                    writer.writerow(
                        [
                            user.username,
                            user.email,
                            getattr(user, "first_name", ""),
                            getattr(user, "last_name", ""),
                            getattr(user, "is_staff", False),
                            user.date_joined.isoformat() if hasattr(user, "date_joined") else "",
                            user.last_login.isoformat() if hasattr(user, "last_login") and user.last_login else "",
                            ", ".join(patterns),
                        ]
                    )

            self.stdout.write(f"✅ Results exported to: {filename}")

        except Exception as e:
            self.stdout.write(f"❌ Error exporting CSV: {e}")

    def _check_email_configuration(self, force_email=False):
        """Check if email is properly configured."""
        from django.conf import settings
        from django.core.mail import get_connection

        if force_email:
            return True

        # Check if email backend is configured (not console backend in production)
        email_backend = getattr(settings, "EMAIL_BACKEND", "")
        if "console" in email_backend.lower():
            self.stdout.write(f"⚠️  Warning: Using console email backend ({email_backend})")
            return False

        # Check if required email settings are configured
        required_settings = ["DEFAULT_FROM_EMAIL"]
        missing_settings = []

        for setting in required_settings:
            if not getattr(settings, setting, None):
                missing_settings.append(setting)

        if missing_settings:
            self.stdout.write(f"❌ Missing email settings: {', '.join(missing_settings)}")
            return False

        # Test email connection
        try:
            connection = get_connection()
            connection.open()
            connection.close()
            return True
        except Exception as e:
            self.stdout.write(f"❌ Email connection test failed: {e}")
            return False

    def _handle_account_deactivation(self, users, dry_run=False):
        """Handle account deactivation for users with weak passwords."""
        self.stdout.write(f"\n🚨 Account Deactivation {'(DRY RUN)' if dry_run else '(LIVE)'}")

        if not dry_run:
            # Safety check - require explicit confirmation
            self.stdout.write(f"⚠️  WARNING: This will deactivate {len(users)} user accounts!")
            response = input("Type 'DEACTIVATE' to confirm: ")
            if response != "DEACTIVATE":
                self.stdout.write("❌ Account deactivation cancelled")
                return

        deactivated_count = 0
        for user in users:
            if not dry_run:
                user.is_active = False
                user.save(update_fields=["is_active"])

            deactivated_count += 1
            self.stdout.write(f"  {'Would deactivate' if dry_run else 'Deactivated'}: {user.username} ({user.email})")

        self.stdout.write(f"🔒 {'Would deactivate' if dry_run else 'Deactivated'} {deactivated_count} accounts")

    def _send_weak_password_notifications(self, users):
        """Send general weak password notifications to users."""
        from django.conf import settings
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        sent_count = 0
        failed_count = 0

        self.stdout.write("\n📧 Sending weak password notifications...")

        for user in users:
            if not user.email:
                self.stdout.write(f"  ⚠️  Skipping {user.username} - no email address")
                continue

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
                self.stdout.write(f"  ✅ Sent to {user.username} ({user.email})")

            except Exception as e:
                self.stdout.write(f"  ❌ Failed to send to {user.email}: {e}")
                failed_count += 1

        self.stdout.write(f"📧 Weak password notifications sent: {sent_count}")
        if failed_count:
            self.stdout.write(f"❌ Failed notifications: {failed_count}")

    def _send_password_reset_emails(self, users):
        """Send password reset emails to users with weak passwords."""
        from django.conf import settings
        from django.contrib.auth.tokens import default_token_generator
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        sent_count = 0
        failed_count = 0

        self.stdout.write("\n🔑 Sending password reset emails...")

        for user in users:
            if not user.email:
                self.stdout.write(f"  ⚠️  Skipping {user.username} - no email address")
                continue

            try:
                # Generate reset token
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
                self.stdout.write(f"  ✅ Reset sent to {user.username} ({user.email})")

            except Exception as e:
                self.stdout.write(f"  ❌ Failed to send reset to {user.email}: {e}")
                failed_count += 1

        self.stdout.write(f"🔑 Password reset emails sent: {sent_count}")
        if failed_count:
            self.stdout.write(f"❌ Failed resets: {failed_count}")

    def _send_security_breach_notifications(self, users):
        """Send security breach notifications to users."""
        from django.conf import settings
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        sent_count = 0
        failed_count = 0

        self.stdout.write("\n🚨 Sending security breach notifications...")

        for user in users:
            if not user.email:
                self.stdout.write(f"  ⚠️  Skipping {user.username} - no email address")
                continue

            try:
                context = {
                    "user": user,
                    "site_name": getattr(settings, "SITE_NAME", "Our Website"),
                    "site_url": getattr(settings, "SITE_URL", "https://yoursite.com"),
                    "support_email": getattr(settings, "SUPPORT_EMAIL", settings.DEFAULT_FROM_EMAIL),
                    "is_staff": getattr(user, "is_staff", False),
                }

                subject = render_to_string("shuup/emails/security_breach_notification_subject.txt", context).strip()
                message = render_to_string("shuup/emails/security_breach_notification.txt", context)
                html_message = render_to_string("shuup/emails/security_breach_notification.html", context)

                send_mail(
                    subject=subject,
                    message=message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                sent_count += 1
                self.stdout.write(f"  ✅ Breach notice sent to {user.username} ({user.email})")

            except Exception as e:
                self.stdout.write(f"  ❌ Failed to send breach notice to {user.email}: {e}")
                failed_count += 1

        self.stdout.write(f"🚨 Security breach notifications sent: {sent_count}")
        if failed_count:
            self.stdout.write(f"❌ Failed breach notifications: {failed_count}")

    def _show_recommendations(self, weak_count, total_count):
        """Show recommendations based on analysis results."""
        self.stdout.write("\n💡 Recommendations:")

        if weak_count == 0:
            self.stdout.write("✅ No users with obviously weak passwords detected!")
            self.stdout.write("   However, this is heuristic analysis. Consider periodic password audits.")

        elif weak_count < total_count * 0.05:  # Less than 5%
            self.stdout.write("✅ Relatively few users with weak passwords detected.")
            self.stdout.write("   Consider targeted notifications to these users.")

        elif weak_count < total_count * 0.20:  # Less than 20%
            self.stdout.write("⚠️  Moderate number of users with potentially weak passwords.")
            self.stdout.write("   Consider implementing forced password reset middleware.")

        else:  # 20% or more
            self.stdout.write("🚨 High number of users with potentially weak passwords!")
            self.stdout.write("   Strongly recommend implementing forced password reset for all users.")

        self.stdout.write("\n🔧 Next steps:")
        self.stdout.write("1. Enable WeakPasswordInterceptMiddleware in settings")
        self.stdout.write("2. Add weak password detection authentication backend")
        self.stdout.write("3. Test forced password reset flow")
        self.stdout.write("4. Consider gradual rollout for large user bases")
        self.stdout.write("5. Monitor password update compliance")

        if weak_count > 0:
            # Get the command used to run this script for copy-paste convenience
            import os
            import sys

            # Determine the command based on how the script was invoked
            script_name = sys.argv[0]
            if script_name.endswith("manage.py"):
                # Direct invocation: python manage.py or ./manage.py
                if script_name.startswith("./"):
                    cmd_prefix = "./manage.py"
                else:
                    cmd_prefix = f"{sys.executable} manage.py"
            elif "shuup_workbench" in script_name or "uv" in script_name or "UV_RUN" in os.environ:
                # UV invocation or shuup_workbench command
                cmd_prefix = "uv run shuup_workbench"
            elif "django-admin" in script_name:
                # Django-admin invocation
                cmd_prefix = "django-admin"
            else:
                # Fallback to python manage.py
                cmd_prefix = f"{sys.executable} manage.py"

            self.stdout.write("\n📝 Command examples (copy-paste ready):")
            self.stdout.write("   Export to CSV:")
            self.stdout.write(f"     {cmd_prefix} identify_weak_passwords --export-csv weak_users.csv")
            self.stdout.write("   ")
            self.stdout.write("   Send notifications:")
            self.stdout.write(f"     {cmd_prefix} identify_weak_passwords --email-notify")
            self.stdout.write(f"     {cmd_prefix} identify_weak_passwords --email-reset")
            self.stdout.write(f"     {cmd_prefix} identify_weak_passwords --email-security-breach")
            self.stdout.write("   ")
            self.stdout.write("   Targeted analysis:")
            self.stdout.write(f"     {cmd_prefix} identify_weak_passwords --staff-only")
            self.stdout.write(f"     {cmd_prefix} identify_weak_passwords --exclude-staff")
            self.stdout.write("   ")
            self.stdout.write("   Emergency actions (use with caution):")
            self.stdout.write(f"     {cmd_prefix} identify_weak_passwords --deactivate-accounts --dry-run")
            self.stdout.write(f"     {cmd_prefix} identify_weak_passwords --deactivate-accounts")
            self.stdout.write("   ")
            self.stdout.write("   Test email without full configuration:")
            self.stdout.write(f"     {cmd_prefix} identify_weak_passwords --email-notify --force-email")

            self.stdout.write("\n⚠️  Email Configuration Required:")
            self.stdout.write("   - Set EMAIL_BACKEND (not console for production)")
            self.stdout.write("   - Configure SMTP settings (HOST, PORT, USER, PASSWORD)")
            self.stdout.write("   - Set DEFAULT_FROM_EMAIL")
            self.stdout.write("   - Optional: Set SITE_NAME, SITE_URL, SUPPORT_EMAIL")
