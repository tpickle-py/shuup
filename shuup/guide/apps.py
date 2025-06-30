import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.guide"
    verbose_name = "Shuup Guide"
    provides = {
        "admin_module": ["shuup.guide.admin_module:GuideAdminModule"],
    }
