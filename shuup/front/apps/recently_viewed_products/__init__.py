from django.utils.translation import ugettext_lazy as _

import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = __name__
    verbose_name = _("Shuup Frontend - Recently Viewed Products")
    label = "shuup_front_recently_viewed_products"

    provides = {
        "xtheme_plugin": [
            __name__ + ".plugins:RecentlyViewedProductsPlugin",
        ],
        "xtheme_resource_injection": [__name__ + ".plugins:add_resources"],
    }


default_app_config = __name__ + ".AppConfig"
