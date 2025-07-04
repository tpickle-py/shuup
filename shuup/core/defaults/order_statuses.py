from shuup.core.models import OrderStatusManager


def create_default_order_statuses():
    manager = OrderStatusManager()
    manager.ensure_default_statuses()
