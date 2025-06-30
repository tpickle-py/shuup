

from django.utils.translation import ugettext_lazy as _

import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = __name__
    verbose_name = _("Shuup Frontend - Personal Order History")
    label = "shuup_front_personal_order_history"

    provides = {
        "front_urls": [__name__ + ".urls:urlpatterns"],
        "customer_dashboard_items": [__name__ + ".dashboard_items:OrderHistoryItem"],
    }


default_app_config = __name__ + ".AppConfig"
