from django.db import models

from shuup.core.models import ShopProduct


class CatalogFilterCachedShopProduct(models.Model):
    filter = models.ForeignKey(
        on_delete=models.CASCADE,
        to="CatalogFilter",
        related_name="cached_shop_products",
        db_index=True,
    )
    shop_product = models.ForeignKey(
        on_delete=models.CASCADE,
        to=ShopProduct,
        related_name="cached_catalog_campaign_filters",
        db_index=True,
    )
