from django.dispatch import Signal

view_form_valid = Signal(use_caching=True)
object_created = Signal(use_caching=True)
object_saved = Signal(use_caching=True)
form_post_clean = Signal(use_caching=True)
form_pre_clean = Signal(use_caching=True)
product_copied = Signal(use_caching=True)
