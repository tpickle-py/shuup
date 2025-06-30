from shuup.apps import AppConfig

from .manager import add_enabled_addons

__all__ = ["add_enabled_addons"]


class ShuupAddonsAppConfig(AppConfig):
    name = "shuup.addons"
    verbose_name = "Shuup Addons"
    label = "shuup_addons"

    provides = {
        "admin_module": [
            "shuup.addons.admin_module:AddonModule",
        ]
    }


default_app_config = "shuup.addons.ShuupAddonsAppConfig"
