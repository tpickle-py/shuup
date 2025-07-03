from django.utils.translation import gettext_lazy as _

import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = __name__
    verbose_name = _("Import")
    label = "importer"

    provides = {
        "admin_module": ["shuup.importer.admin_module:ImportAdminModule"],
    }
