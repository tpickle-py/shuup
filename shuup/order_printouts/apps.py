from django.utils.translation import ugettext_lazy as _

import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.order_printouts"
    verbose_name = _("Order printouts")
    label = "shuup_order_printouts"

    provides = {
        "admin_module": ["shuup.order_printouts.admin_module:PrintoutsAdminModule"],
        "admin_order_section": ["shuup.order_printouts.admin_module.section:PrintoutsSection"],
    }
