

from django.utils.translation import ugettext_lazy as _

import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.default_tax"
    verbose_name = _("Shuup Default Tax")
    label = "default_tax"
    default_auto_field = "django.db.models.BigAutoField"

    provides = {
        "tax_module": ["shuup.default_tax.module:DefaultTaxModule"],
        "admin_module": ["shuup.default_tax.admin_module:TaxRulesAdminModule"],
    }


default_app_config = __name__ + ".AppConfig"
