"""
Views for handling forced password resets due to weak passwords.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from shuup.core.utils.weak_password_detection import (
    mark_password_as_updated,
    should_force_password_reset,
)


@method_decorator(login_required, name="dispatch")
class ForcedPasswordResetView(FormView):
    """
    View for forced password reset when weak password is detected.

    This view forces users with weak passwords to update their passwords
    before they can continue using the system.
    """

    template_name = "shuup/auth/forced_password_reset.jinja"
    form_class = SetPasswordForm
    success_url = reverse_lazy("shuup:index")

    def dispatch(self, request, *args, **kwargs):
        """
        Check if user actually needs forced password reset.
        """
        if not should_force_password_reset(request.user):
            # User doesn't need forced reset, redirect to home
            return redirect("shuup:index")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Add user to form kwargs.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Add context for template.
        """
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": _("Security: Password Update Required"),
                "user": self.request.user,
                "is_forced_reset": True,
            }
        )
        return context

    def form_valid(self, form):
        """
        Handle successful password update.
        """
        user = form.save()

        # Clear the weak password flag
        mark_password_as_updated(user)

        # Update the session to prevent logout
        # This keeps the user logged in with their new password
        from django.contrib.auth import update_session_auth_hash

        update_session_auth_hash(self.request, user)

        messages.success(
            self.request, _("Your password has been successfully updated. You can now continue using the system.")
        )

        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle invalid password update.
        """
        messages.error(self.request, _("Please correct the errors below and choose a strong password."))
        return super().form_invalid(form)


class SecurePasswordChangeView(PasswordChangeView):
    """
    Enhanced password change view with weak password detection.

    This view extends Django's standard password change view to clear
    weak password flags when users successfully update their passwords.
    """

    template_name = "shuup/customer_information/change_password.jinja"
    success_url = reverse_lazy("shuup:customer_edit")

    def form_valid(self, form):
        """
        Handle successful password change.
        """
        response = super().form_valid(form)

        # Clear any weak password flags since user updated their password
        mark_password_as_updated(self.request.user)

        messages.success(
            self.request, _("Your password has been successfully changed and now meets our security requirements.")
        )

        return response


def check_weak_password_status(request):
    """
    AJAX endpoint to check if user needs forced password reset.

    This can be used by frontend JavaScript to check password status
    without triggering middleware redirects.
    """
    from django.http import JsonResponse

    if not request.user.is_authenticated:
        return JsonResponse({"needs_reset": False, "error": "Not authenticated"})

    needs_reset = should_force_password_reset(request.user)

    return JsonResponse(
        {
            "needs_reset": needs_reset,
            "message": _("Password update required for security") if needs_reset else _("Password is secure"),
        }
    )


def emergency_password_reset(request):
    """
    Emergency password reset for cases where middleware might not work properly.

    This provides a fallback mechanism for users who might get stuck
    in redirect loops or other edge cases.
    """
    if not request.user.is_authenticated:
        return redirect("shuup:auth.login")

    if request.method == "POST":
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            mark_password_as_updated(user)

            # Update session to keep user logged in
            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(request, user)

            messages.success(request, _("Password updated successfully."))
            return redirect("shuup:index")
    else:
        form = SetPasswordForm(request.user)

    return render(
        request,
        "shuup/auth/emergency_password_reset.jinja",
        {
            "form": form,
            "title": _("Emergency Password Reset"),
        },
    )
