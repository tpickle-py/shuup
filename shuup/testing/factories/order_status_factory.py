# Django 3+ compatible OrderStatus helper functions
# Replaces the TODO functions from factories.py.moved

from shuup.core.defaults.order_statuses import create_default_order_statuses
from shuup.core.models import OrderStatus


def get_initial_order_status():
    """Get the default initial order status, Django 3+ compatible."""
    create_default_order_statuses()
    # These methods are confirmed to exist in Django 3+
    return OrderStatus.objects.get_default_initial()


def get_completed_order_status():
    """Get the default completed order status, Django 3+ compatible."""
    create_default_order_statuses()
    # These methods are confirmed to exist in Django 3+
    return OrderStatus.objects.get_default_complete()


def get_processing_order_status():
    """Get the default processing order status."""
    create_default_order_statuses()
    return OrderStatus.objects.get_default_processing()


def get_canceled_order_status():
    """Get the default canceled order status."""
    create_default_order_statuses()
    return OrderStatus.objects.get_default_canceled()
