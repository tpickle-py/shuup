from django.core.signals import Signal

post_compute_source_lines = Signal(providing_args=["source", "lines"], use_caching=True)
order_creator_finished = Signal(providing_args=["order", "source"], use_caching=True)
post_order_line_save = Signal(providing_args=["order_line", "order"], use_caching=True)
