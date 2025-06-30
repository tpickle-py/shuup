from django.dispatch import Signal

# triggered when a shop product must be indexed
index_catalog_shop_product = Signal(providing_args=["shop_product"])
