import random

from django.conf import settings
from django.utils import translation

from shuup.core.models import Category, Product, ShopProduct

from .factories import (
    CategoryFactory,
    ProductFactory,
    create_default_order_statuses,
    get_currency,
    get_default_customer_group,
    get_default_payment_method,
    get_default_shipping_method,
    get_default_shop,
)


class Populator:
    def __init__(self):
        self.shop = get_default_shop()

    def populate(self):
        translation.activate(settings.LANGUAGES[0][0])

        # Create default objects
        get_default_payment_method()
        get_default_shipping_method()
        create_default_order_statuses()
        get_currency("EUR")
        get_currency("USD")
        get_currency("BRL")
        get_currency("GBP")
        get_currency("CNY")
        get_currency("JPY", digits=0)

        category_created = False
        while Category.objects.count() < 5:
            CategoryFactory()
            category_created = True

        if category_created:
            Category.objects.rebuild()

        while Product.objects.count() < 30:
            product = ProductFactory()
            self.generate_pricing(product)

        # Ensure all products are associated with the default shop
        self.ensure_shop_products()

    def generate_pricing(self, product):
        if "shuup.customer_group_pricing" in settings.INSTALLED_APPS:
            try:
                from shuup.customer_group_pricing.models import CgpPrice

                CgpPrice.objects.create(
                    product=product,
                    price_value=random.randint(15, 340),
                    shop=get_default_shop(),
                    group=get_default_customer_group(),
                )
            except Exception:
                # If customer_group_pricing is not properly set up, skip pricing
                pass

    def ensure_shop_products(self):
        """Ensure all products are associated with the default shop."""
        from shuup.core.models import ShopProduct

        # Get all products without shop associations in the default shop
        products_without_shop = Product.objects.exclude(shop_products__shop=self.shop)

        for product in products_without_shop:
            ShopProduct.objects.get_or_create(
                shop=self.shop,
                product=product,
                defaults={
                    "purchasable": True,
                    "visibility": 3,  # ALWAYS_VISIBLE
                    "default_price_value": 50.0,
                },
            )

    def populate_if_required(self):
        if ShopProduct.objects.filter(shop=self.shop).count() < 5:
            self.populate()

        # Ensure products have stock for purchasability
        self.ensure_product_stock()

        # Try to reindex product catalog, but don't fail if there are table issues
        try:
            from django.core.management import call_command

            call_command("reindex_product_catalog")
        except Exception:
            # If reindexing fails due to missing tables, skip it
            pass

    def ensure_product_stock(self):
        """Ensure all shop products have sufficient stock for testing."""
        from shuup.core.models import Supplier

        try:
            supplier = Supplier.objects.first()
            if not supplier:
                return

            shop_products = ShopProduct.objects.filter(shop=self.shop)
            for shop_product in shop_products:
                try:
                    # Check current stock
                    stock_status = supplier.get_stock_status(shop_product.product.id)
                    if stock_status.logical_count <= 0:
                        # Add stock for testing (100 units)
                        supplier.adjust_stock(shop_product.product.id, 100)
                except Exception:
                    # If stock management fails, skip this product
                    continue
        except Exception:
            # If stock management is not available, skip entirely
            pass


def populate_if_required():
    Populator().populate_if_required()
