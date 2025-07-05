import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import DatabaseError, transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from shuup.core.utils.weak_password_detection import check_user_against_weak_patterns, get_weak_password_patterns

logger = logging.getLogger(__name__)


@method_decorator(staff_member_required, name="dispatch")
class SecurityDashboardView(TemplateView):
    """
    Main security dashboard showing overview metrics and quick actions.
    Only accessible to admin staff.
    """

    template_name = "shuup/admin/security/dashboard.jinja"
    cache_timeout = 900  # 15 minutes

    def dispatch(self, request, *args, **kwargs):
        """Ensure only staff with proper permissions can access."""
        user = request.user

        if not user.is_authenticated:
            messages.error(request, _("You must be logged in to access the security dashboard."))
            return redirect("shuup_admin:login")

        if not getattr(user, "is_staff", False):
            messages.error(request, _("Access denied. Admin privileges required."))
            return redirect("shuup_admin:dashboard")

        return super().dispatch(request, *args, **kwargs)

    def _get_recent_security_actions(self):
        """Get recent security-related actions/events."""
        # TODO: Replace with actual log retrieval logic
        return [
            {
                "timestamp": datetime.now() - timedelta(hours=2),
                "action": "Password policy updated",
                "user": "admin",
                "details": "Enabled strong password validation",
            },
            {
                "timestamp": datetime.now() - timedelta(hours=6),
                "action": "Weak passwords identified",
                "user": "system",
                "details": "5 users flagged for password reset",
            },
            {
                "timestamp": datetime.now() - timedelta(days=1),
                "action": "Security notifications sent",
                "user": "admin",
                "details": "Email alerts sent to 3 users",
            },
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Get cached metrics or calculate them
            cache_key = "security_dashboard_metrics"
            metrics = cache.get(cache_key)

            if not metrics:
                metrics = self._calculate_security_metrics()
                cache.set(cache_key, metrics, self.cache_timeout)

            context.update(
                {
                    "title": _("Security Dashboard"),
                    "metrics": metrics,
                    "weak_password_patterns": get_weak_password_patterns()[:10],
                    "recent_security_actions": self._get_recent_security_actions(),
                }
            )
        except (AttributeError, ValueError, DatabaseError) as e:
            msg = _(f"{e} - Error loading security dashboard data. Please try again later.")
            logger.error(msg)
            messages.error(self.request, _("Error loading dashboard data. Please try again."))
            context.update(
                {
                    "title": _("Security Dashboard"),
                    "metrics": {},
                    "weak_password_patterns": [],
                    "recent_security_actions": [],
                }
            )

        return context

    def _calculate_security_metrics(self):
        """Calculate security metrics for the dashboard with optimized queries."""
        user_model = get_user_model()

        try:
            # Optimize with select_related and prefetch_related if needed
            active_users = user_model.objects.filter(is_active=True)

            # Basic user counts - use database aggregation
            total_users = active_users.count()
            staff_users = active_users.filter(is_staff=True).count()
            regular_users = total_users - staff_users

            # Optimize weak password analysis
            weak_password_metrics = self._analyze_weak_passwords(active_users)

            # User activity metrics (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_logins = active_users.filter(last_login__gte=thirty_days_ago).count()

            # Calculate risk assessment
            risk_data = self._calculate_risk_level(weak_password_metrics["weak_password_percentage"])

            return {
                "total_users": total_users,
                "staff_users": staff_users,
                "regular_users": regular_users,
                "recent_logins": recent_logins,
                "users_without_recent_login": total_users - recent_logins,
                **weak_password_metrics,
                **risk_data,
            }
        except (DatabaseError, ValueError, AttributeError) as e:
            msg = _(f"{e} - Error calculating security metrics. Please try again later.")
            logger.error(msg)
            return self._get_default_metrics()

    def _analyze_weak_passwords(self, users_queryset):
        """Analyze users for weak passwords with optimized approach."""
        weak_staff_count = 0
        weak_regular_count = 0
        total_users = users_queryset.count()

        # Batch process users to avoid memory issues with large datasets
        batch_size = 1000
        weak_password_count = 0

        for i in range(0, total_users, batch_size):
            batch_users = users_queryset[i : i + batch_size]

            for user in batch_users:
                if check_user_against_weak_patterns(user):
                    weak_password_count += 1
                    if getattr(user, "is_staff", False):
                        weak_staff_count += 1
                    else:
                        weak_regular_count += 1

        weak_password_percentage = (weak_password_count / total_users * 100) if total_users > 0 else 0

        return {
            "weak_password_count": weak_password_count,
            "weak_staff_count": weak_staff_count,
            "weak_regular_count": weak_regular_count,
            "weak_password_percentage": round(weak_password_percentage, 1),
        }

    def _calculate_risk_level(self, weak_password_percentage):
        """Calculate risk level based on weak password percentage."""
        if weak_password_percentage >= 30:
            return {"risk_level": "critical", "risk_label": _("Critical"), "risk_color": "danger"}
        elif weak_password_percentage >= 15:
            return {"risk_level": "high", "risk_label": _("High"), "risk_color": "warning"}
        elif weak_password_percentage >= 5:
            return {"risk_level": "medium", "risk_label": _("Medium"), "risk_color": "info"}
        else:
            return {"risk_level": "low", "risk_label": _("Low"), "risk_color": "success"}

    def _get_default_metrics(self):
        """Return default metrics when calculation fails."""
        return {
            "total_users": 0,
            "staff_users": 0,
            "regular_users": 0,
            "weak_password_count": 0,
            "weak_staff_count": 0,
            "weak_regular_count": 0,
            "weak_password_percentage": 0,
            "risk_level": "unknown",
            "risk_label": _("Unknown"),
            "risk_color": "secondary",
            "recent_logins": 0,
            "users_without_recent_login": 0,
        }

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Handle AJAX requests for dashboard actions."""
        action = request.POST.get("action")

        if action == "refresh_metrics":
            return self._handle_refresh_metrics()
        elif action == "quick_scan":
            return self._handle_quick_scan()

        return JsonResponse({"success": False, "message": str(_("Invalid action."))})

    def _handle_refresh_metrics(self):
        """Handle metrics refresh action."""
        cache.delete("security_dashboard_metrics")
        metrics = self._calculate_security_metrics()
        cache.set("security_dashboard_metrics", metrics, self.cache_timeout)

        return JsonResponse(
            {"success": True, "metrics": metrics, "message": str(_("Security metrics refreshed successfully."))}
        )

    def _handle_quick_scan(self):
        """Handle quick security scan action."""
        user_model = get_user_model()
        weak_users = []

        try:
            active_users = user_model.objects.filter(is_active=True)

            for user in active_users:
                user_id = getattr(user, "id", None)
                user_username = getattr(user, "username", None)
                user_email = getattr(user, "email", None)
                if self._is_user_data_valid(user) and check_user_against_weak_patterns(user):
                    weak_users.append(
                        {
                            "id": user_id,
                            "username": user_username,
                            "email": user_email,
                            "is_staff": getattr(user, "is_staff", False),
                        }
                    )

            return JsonResponse(
                {
                    "success": True,
                    "weak_users": weak_users,
                    "count": len(weak_users),
                    "message": str(_("Security scan completed.")),
                }
            )
        except (DatabaseError, ValueError, AttributeError) as e:
            msg = _(f"{e} - Error during quick security scan. Please try again later.")
            logger.error(msg)
            return JsonResponse({"success": False, "message": str(_("Error during security scan. Please try again."))})

    def _is_user_data_valid(self, user):
        """Check if user has valid required data."""
        return all(
            [
                getattr(user, "id", None) is not None,
                getattr(user, "username", None) is not None,
                getattr(user, "email", None) is not None,
            ]
        )
