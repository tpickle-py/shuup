from django.core.management.base import BaseCommand

from shuup.core.catalog import ProductCatalog
from shuup.core.models import ProductMode, ShopProduct


class Command(BaseCommand):
    help = "Reindex the prices and availability of all products of the catalog"

    def handle(self, *args, **options):
        for shop_product in ShopProduct.objects.exclude(product__mode=ProductMode.VARIATION_CHILD):
            ProductCatalog.index_shop_product(shop_product)
