from shuup.apps import AppConfig


class ShuupSimpleSupplierAppConfig(AppConfig):
    name = "shuup.simple_supplier"
    verbose_name = "Shuup Simple Supplier"
    label = "simple_supplier"
    default_auto_field = "django.db.models.BigAutoField"
    provides = {
        "supplier_module": ["shuup.simple_supplier.module:SimpleSupplierModule"],
        "admin_product_form_part": ["shuup.simple_supplier.admin_module.forms:SimpleSupplierFormPart"],
        "admin_module": ["shuup.simple_supplier.admin_module:StocksAdminModule"],
        "notify_event": ["shuup.simple_supplier.notify_events:AlertLimitReached"],
        "notify_script_template": [
            "shuup.simple_supplier.notify_script_template:StockLimitEmailScriptTemplate",
        ],
    }

    def ready(self):
        import shuup.simple_supplier.product_copy_signal_handler  # noqa: F401
        import shuup.simple_supplier.signal_handlers  # noqa: F401


default_app_config = "shuup.simple_supplier.ShuupSimpleSupplierAppConfig"
