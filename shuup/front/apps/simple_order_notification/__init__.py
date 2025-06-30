from shuup.apps import AppConfig


class SimpleOrderNotificationAppConfig(AppConfig):
    name = "shuup.front.apps.simple_order_notification"
    verbose_name = "Shuup Frontend - Simple Order Notification"
    label = "shuup_front_simple_order_notification"

    provides = {
        "admin_module": [
            "shuup.front.apps.simple_order_notification.admin_module:SimpleOrderNotificationModule",
        ]
    }


default_app_config = (
    "shuup.front.apps.simple_order_notification.SimpleOrderNotificationAppConfig"
)
