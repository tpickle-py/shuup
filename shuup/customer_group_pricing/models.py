from django.db import models
from django.utils.translation import gettext_lazy as _

from shuup.core.fields import MoneyValueField
from shuup.core.utils.context_cache import bump_cache_for_product
from shuup.utils.properties import MoneyPropped, PriceProperty


class CgpBase(models.Model):
    product = models.ForeignKey(
        "shuup.Product",
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name=_("product"),
    )
    shop = models.ForeignKey("shuup.Shop", db_index=True, on_delete=models.CASCADE, verbose_name=_("shop"))
    group = models.ForeignKey(
        "shuup.ContactGroup",
        db_index=True,
        on_delete=models.CASCADE,
        verbose_name=_("contact group"),
    )

    class Meta:
        abstract = True
        unique_together = (("product", "shop", "group"),)


class CgpPrice(MoneyPropped, CgpBase):
    price = PriceProperty("price_value", "shop.currency", "shop.prices_include_tax")
    price_value = MoneyValueField(verbose_name=_("price"))

    class Meta(CgpBase.Meta):
        abstract = False
        verbose_name = _("product price")
        verbose_name_plural = _("product prices")

    def __repr__(self):
        return f"<CgpPrice (p{self.product_id},s{self.shop_id},g{self.group_id}): price {self.price}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # check if there is a shop product before bumping the cache
        if self.product.shop_products.filter(shop_id=self.shop.id).exists():
            bump_cache_for_product(self.product, self.shop)


class CgpDiscount(MoneyPropped, CgpBase):
    discount_amount = PriceProperty("discount_amount_value", "shop.currency", "shop.prices_include_tax")
    discount_amount_value = MoneyValueField(verbose_name=_("discount amount"))

    class Meta(CgpBase.Meta):
        abstract = False
        verbose_name = _("product discount")
        verbose_name_plural = _("product discounts")

    def __repr__(self):
        return f"<CgpDiscount (p{self.product_id},s{self.shop_id},g{self.group_id}): discount {self.discount_amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # check if there is a shop product before bumping the cache
        if self.product.shop_products.filter(shop_id=self.shop.id).exists():
            bump_cache_for_product(self.product, self.shop)
