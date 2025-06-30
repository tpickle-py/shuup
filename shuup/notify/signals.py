
from django.dispatch import Signal

notification_email_before_send = Signal(providing_args=["action", "message", "context"])
notification_email_sent = Signal(providing_args=["message", "context"])
