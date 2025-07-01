from django.dispatch import receiver

from shuup.admin.signals import product_copied
from shuup.simple_supplier.models import StockCount


@receiver(product_copied, dispatch_uid="simple_supplier_product_copied")
def handle_product_copy(sender, shop, copied, copy, supplier=None, **kwargs):
    shop_product = copied.get_shop_instance(shop)

    for supplier in shop_product.suppliers.all():
        origin_product_stock_count = StockCount.objects.get_or_create(supplier=supplier, product=copied)[0]
        new_product_stock_count = StockCount.objects.get_or_create(supplier=supplier, product=copy)[0]
        new_product_stock_count.stock_managed = origin_product_stock_count.stock_managed
        new_product_stock_count.save(update_fields=["stock_managed"])
