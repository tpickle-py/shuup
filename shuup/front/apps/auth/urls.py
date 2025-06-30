from django.conf.urls import url

from shuup.core.utils.maintenance import maintenance_mode_exempt

from .views import (
    LoginView,
    LogoutView,
    RecoverPasswordCompleteView,
    RecoverPasswordConfirmView,
    RecoverPasswordSentView,
    RecoverPasswordView,
)

urlpatterns = [
    url(r"^login/$", LoginView.as_view(), name="login"),
    url(r"^logout/$", LogoutView.as_view(), name="logout"),
    url(r"^recover-password/$", RecoverPasswordView.as_view(), name="recover_password"),
    url(
        r"^recover-password/(?P<uidb64>.+)/(?P<token>.+)/$",
        maintenance_mode_exempt(RecoverPasswordConfirmView.as_view()),
        name="recover_password_confirm",
    ),
    url(
        r"^recover-password/sent/$",
        RecoverPasswordSentView.as_view(),
        name="recover_password_sent",
    ),
    url(
        r"^recover-password/complete/$",
        maintenance_mode_exempt(RecoverPasswordCompleteView.as_view()),
        name="recover_password_complete",
    ),
]
