from django.utils.translation import gettext_lazy as _

import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = __name__
    verbose_name = _("Shuup Frontend - Customer Information Editing")
    label = "shuup_front_customer_information"

    provides = {
        "front_urls": [__name__ + ".urls:urlpatterns"],
        "customer_dashboard_items": [
            __name__ + ".dashboard_items:CustomerDashboardItem",
            __name__ + ".dashboard_items:CompanyDashboardItem",
            __name__ + ".dashboard_items:AddressBookDashboardItem",
        ],
        "notify_event": ["shuup.front.apps.customer_information.notify_events:CompanyAccountCreated"],
    }


default_app_config = __name__ + ".AppConfig"
