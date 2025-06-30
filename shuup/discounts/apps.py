import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup.discounts"
    default_auto_field = "django.db.models.BigAutoField"
    provides = {
        "admin_module": [
            "shuup.discounts.admin.modules.DiscountModule",
            "shuup.discounts.admin.modules.DiscountArchiveModule",
            "shuup.discounts.admin.modules.HappyHourModule",
        ],
        "admin_object_selector": [
            "shuup.discounts.admin.object_selector.DiscountAdminObjectSelector",
        ],
        "discount_module": ["shuup.discounts.modules:ProductDiscountModule"],
        "xtheme_plugin": ["shuup.discounts.plugins:DiscountedProductsPlugin"],
    }

    def ready(self):
        import shuup.discounts.signal_handlers  # noqa: F401
