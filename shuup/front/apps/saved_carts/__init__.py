from django.utils.translation import gettext_lazy as _

import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = __name__
    verbose_name = _("Shuup Frontend - Saved Baskets")
    label = "shuup_front_saved_baskets"

    provides = {
        "front_urls": [__name__ + ".urls:urlpatterns"],
        "customer_dashboard_items": [__name__ + ".dashboard_items:SavedCartsItem"],
    }


default_app_config = __name__ + ".AppConfig"
