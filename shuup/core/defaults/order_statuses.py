from shuup.core.models import OrderStatusManager


def create_default_order_statuses():
    OrderStatusManager().ensure_default_statuses()
