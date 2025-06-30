import django.contrib.auth.views as auth_views

from shuup.utils.importing import cached_load


class LogoutView(auth_views.LogoutView):
    template_name = "shuup/admin/auth/logout.jinja"


class LoginView(auth_views.LoginView):
    form_class = cached_load("SHUUP_ADMIN_AUTH_FORM_SPEC")
