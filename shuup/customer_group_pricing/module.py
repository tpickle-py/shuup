from decimal import Decimal
from typing import Union

from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from shuup.core.models import (
    AnonymousContact,
    ProductCatalogDiscountedPrice,
    ProductCatalogDiscountedPriceRule,
    ProductCatalogPrice,
    ProductCatalogPriceRule,
    ShopProduct,
    Supplier,
)
from shuup.core.pricing import DiscountModule, PriceInfo, PricingModule

from .models import CgpDiscount, CgpPrice


class CustomerGroupPricingModule(PricingModule):
    identifier = "customer_group_pricing"
    name = _("Customer Group Pricing")

    def _is_product_available(self, shop_product, supplier_id):
        """
        Check if a product is available for purchase considering stock and orderability.

        This integrates the catalog system with actual stock management and purchasability logic.
        """
        try:
            # Get the supplier instance
            supplier = Supplier.objects.get(pk=supplier_id) if supplier_id else None
            if not supplier:
                return False

            # Ensure backorder_maximum is set to 0 for proper stock checking
            # If backorder_maximum is None, SimpleSupplier allows unlimited backorders
            if shop_product.backorder_maximum is None:
                shop_product.backorder_maximum = 0
                shop_product.save(update_fields=["backorder_maximum"])

            # Use anonymous contact for general availability check
            customer = AnonymousContact()

            # Check if the product is orderable with this supplier
            # This includes stock checks, supplier availability, and all business rules
            is_orderable = shop_product.is_orderable(supplier=supplier, customer=customer, quantity=1)

            return is_orderable

        except Exception:
            # If any error occurs (supplier not found, etc.), default to not available
            return False

    def get_price_info(self, context, product, quantity=1):
        shop = context.shop
        product_id = product if isinstance(product, int) else product.pk
        shop_product = ShopProduct.objects.filter(product_id=product_id, shop=shop).only("default_price_value").first()

        if not shop_product:
            return PriceInfo(
                price=shop.create_price(0),
                base_price=shop.create_price(0),
                quantity=quantity,
            )

        default_price = shop_product.default_price_value or 0
        filter = Q(
            product_id=product_id,
            shop=shop,
            price_value__gt=0,
            group__in=context.customer.groups.all(),
        )
        result = CgpPrice.objects.filter(filter).order_by("price_value")[:1].values_list("price_value", flat=True)

        if result:
            price = result[0]
            if default_price > 0:
                price = min([default_price, price])
        else:
            price = default_price

        return PriceInfo(
            price=shop.create_price(price * quantity),
            base_price=shop.create_price(default_price * quantity),
            quantity=quantity,
        )

    def index_shop_product(self, shop_product: Union["ShopProduct", int], **kwargs):
        if isinstance(shop_product, int):
            shop_product = ShopProduct.objects.select_related("shop", "product").get(pk=shop_product)

        is_variation_parent = shop_product.product.is_variation_parent()

        # index the price of all children shop products
        if is_variation_parent:
            children_shop_product = ShopProduct.objects.select_related("product", "shop").filter(
                shop=shop_product.shop,
                product__variation_parent_id=shop_product.product_id,
            )
            for child_shop_product in children_shop_product:
                self.index_shop_product(child_shop_product)
        else:
            # clean up all prices for this product and shop
            ProductCatalogPrice.objects.filter(
                product_id=shop_product.product_id, shop_id=shop_product.shop_id
            ).delete()

            # index all the prices with groups
            try:
                cgp_prices = CgpPrice.objects.filter(product_id=shop_product.product_id, shop_id=shop_product.shop_id)

                for customer_group_price in cgp_prices:
                    catalog_rule = ProductCatalogPriceRule.objects.get_or_create(
                        module_identifier=self.identifier,
                        contact_group=customer_group_price.group,
                        contact=None,
                    )[0]
                    for supplier_id in shop_product.suppliers.values_list("pk", flat=True):
                        # Check if product is available with this supplier (includes stock and orderability)
                        is_available = self._is_product_available(shop_product, supplier_id)

                        ProductCatalogPrice.objects.update_or_create(
                            product_id=shop_product.product_id,
                            shop_id=shop_product.shop_id,
                            supplier_id=supplier_id,
                            catalog_rule=catalog_rule,
                            defaults={
                                "price_value": customer_group_price.price_value or Decimal(),
                                "is_available": is_available,
                            },
                        )
            except Exception:
                # If CgpPrice table doesn't exist, skip customer group pricing indexing
                pass

        for supplier_id in shop_product.suppliers.values_list("pk", flat=True):
            # Check if product is available with this supplier (includes stock and orderability)
            is_available = self._is_product_available(shop_product, supplier_id)

            # index the default price value
            ProductCatalogPrice.objects.update_or_create(
                product_id=shop_product.product_id,
                shop_id=shop_product.shop_id,
                supplier_id=supplier_id,
                catalog_rule=None,
                defaults={
                    "price_value": shop_product.default_price_value or Decimal(),
                    "is_available": is_available,
                },
            )


class CustomerGroupDiscountModule(DiscountModule):
    identifier = "customer_group_discount"
    name = _("Customer Group Discount")

    def discount_price(self, context, product, price_info):
        """
        Get the best discount amount for context.
        """
        shop = context.shop
        product_id = product if isinstance(product, int) else product.pk

        cgp_discount = (
            CgpDiscount.objects.filter(
                shop_id=shop.id,
                product_id=product_id,
                group__in=context.customer.groups.all(),
                discount_amount_value__gt=0,
            )
            .order_by("-discount_amount_value")
            .first()
        )

        if cgp_discount:
            total_discount = cgp_discount.discount_amount * price_info.quantity
            # do not allow the discount to be greater than the price
            return PriceInfo(
                price=max(price_info.price - total_discount, context.shop.create_price(0)),
                base_price=price_info.base_price,
                quantity=price_info.quantity,
                expires_on=price_info.expires_on,
            )

        return price_info

    def index_shop_product(self, shop_product: Union["ShopProduct", int], **kwargs):
        """
        Index the shop product discounts
        """
        if isinstance(shop_product, int):
            shop_product = ShopProduct.objects.select_related("shop", "product").get(pk=shop_product)

        is_variation_parent = shop_product.product.is_variation_parent()

        # index the discounted price of all children shop products
        if is_variation_parent:
            children_shop_product = ShopProduct.objects.select_related("product", "shop").filter(
                shop=shop_product.shop, product__variation_parent=shop_product.product
            )
            for child_shop_product in children_shop_product:
                self.index_shop_product(child_shop_product)
        else:
            # clear all existing discounted prices for this discount module
            ProductCatalogDiscountedPrice.objects.filter(
                catalog_rule__module_identifier=self.identifier,
                product_id=shop_product.product_id,
                shop_id=shop_product.shop_id,
            ).delete()

            normal_price = shop_product.default_price_value or Decimal()

            # there is no valid price
            if not normal_price:
                return

            # index all the discounted prices
            for customer_group_discount in CgpDiscount.objects.filter(
                product_id=shop_product.product_id, shop_id=shop_product.shop_id
            ):
                catalog_rule = ProductCatalogDiscountedPriceRule.objects.get_or_create(
                    module_identifier=self.identifier,
                    contact_group=customer_group_discount.group,
                    contact=None,
                    valid_start_date=None,
                    valid_end_date=None,
                    valid_start_hour=None,
                    valid_end_hour=None,
                    valid_weekday=None,
                )[0]
                # the discount is always over the default product price
                discounted_price = max(
                    normal_price - customer_group_discount.discount_amount_value,
                    Decimal(),
                )

                for supplier_id in shop_product.suppliers.values_list("pk", flat=True):
                    ProductCatalogDiscountedPrice.objects.update_or_create(
                        product_id=shop_product.product_id,
                        shop_id=shop_product.shop_id,
                        supplier_id=supplier_id,
                        catalog_rule=catalog_rule,
                        defaults={"discounted_price_value": discounted_price},
                    )
