from shuup.apps import AppConfig


class AuthAppConfig(AppConfig):
    name = "shuup.front.apps.auth"
    verbose_name = "Shuup Frontend - User Authentication"
    label = "shuup_front_auth"

    provides = {
        "front_urls": ["shuup.front.apps.auth.urls:urlpatterns"],
    }


default_app_config = "shuup.front.apps.auth.AuthAppConfig"
