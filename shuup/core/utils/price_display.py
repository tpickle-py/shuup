"""
Utilities for displaying prices correctly.

Contents:

  * Class `PriceDisplayOptions` for storing the display options.

  * Helper function `render_price_property` for rendering prices
    correctly from Python code.

  * Various filter classes for implementing Jinja2 filters.
"""

import django_jinja.library

from shuup.compat import contextfilter, contextfunction
from shuup.core.catalog import ProductCatalog, ProductCatalogContext
from shuup.core.pricing import PriceDisplayOptions, Priceful, PriceInfo
from shuup.core.templatetags.shuup_common import money, percent
from shuup.core.utils.price_cache import (
    cache_many_price_info,
    cache_price_info,
    get_cached_price_info,
    get_many_cached_price_info,
)
from shuup.core.utils.prices import convert_taxness

PRICED_CHILDREN_CACHE_KEY = "%s-%s_priced_children"


def render_price_property(request, item, priceful, property_name="price"):
    """
    Render price property of a Priceful object.

    :type request: django.http.HttpRequest
    :type item: shuup.core.taxing.TaxableItem
    :type priceful: shuup.core.pricing.Priceful
    :type propert_name: str
    :rtype: str
    """
    options = PriceDisplayOptions.from_context({"request": request})
    if options.hide_prices:
        return ""
    new_priceful = convert_taxness(request, item, priceful, options.include_taxes)
    price_value = getattr(new_priceful, property_name)
    return money(price_value)


class _ContextObject:
    def __init__(self, name, property_name=None):
        self.name = name
        self.property_name = property_name or name
        self._register()


class _ContextFilter(_ContextObject):
    def _register(self):
        django_jinja.library.filter(name=self.name, fn=contextfilter(self))

    @property
    def cache_identifier(self):
        return f"price_filter_{self.name}"


class _ContextFunction(_ContextObject):
    def _register(self):
        django_jinja.library.global_function(name=self.name, fn=contextfunction(self))


def _get_item_price_info(request, item, quantity, supplier=None):
    # the item has a catalog price annotate, use it
    # this speeds up when using querysets coming from ProductCatalog
    if hasattr(item, "catalog_price") and hasattr(item, "catalog_discounted_price") and item.catalog_price is not None:
        shop = request.shop
        discounted_price = item.catalog_discounted_price if item.catalog_discounted_price is not None else None
        return PriceInfo(
            price=shop.create_price((discounted_price if discounted_price else item.catalog_price) * quantity),
            base_price=shop.create_price(item.catalog_price * quantity),
            quantity=quantity,
        )

    return _get_priceful(request, item, quantity, supplier)


class PriceDisplayFilter(_ContextFilter):
    def __call__(
        self,
        context,
        item,
        quantity=1,
        include_taxes=None,
        allow_cache=True,
        supplier=None,
    ):
        options = PriceDisplayOptions.from_context(context)
        if options.hide_prices:
            return ""

        if include_taxes is None:
            include_taxes = options.include_taxes

        request = context.get("request")

        price_info = (
            get_cached_price_info(request, item, quantity, include_taxes=include_taxes, supplier=supplier)
            if allow_cache
            else None
        )

        if not price_info:
            price_info = _get_item_price_info(request, item, quantity, supplier)

            if not price_info:
                return ""

            price_info = convert_taxness(request, item, price_info, include_taxes)
            if allow_cache:
                cache_price_info(
                    request,
                    item,
                    quantity,
                    price_info,
                    include_taxes=include_taxes,
                    supplier=supplier,
                )

        return money(getattr(price_info, self.property_name))


class PricePropertyFilter(_ContextFilter):
    def __call__(self, context, item, quantity=1, allow_cache=True, supplier=None):
        request = context.get("request")
        price_info = get_cached_price_info(request, item, quantity, supplier=supplier) if allow_cache else None

        if not price_info:
            price_info = _get_item_price_info(request, item, quantity, supplier)

            if not price_info:
                return ""
            if allow_cache:
                cache_price_info(request, item, quantity, price_info, supplier=supplier)

        return getattr(price_info, self.property_name)


class PricePercentPropertyFilter(_ContextFilter):
    def __call__(self, context, item, quantity=1, allow_cache=True, supplier=None):
        request = context.get("request")
        price_info = get_cached_price_info(request, item, quantity, supplier=supplier) if allow_cache else None

        if not price_info:
            price_info = _get_item_price_info(request, item, quantity, supplier)

            if not price_info:
                return ""
            if allow_cache:
                cache_price_info(request, item, quantity, price_info, supplier=supplier)

        return percent(getattr(price_info, self.property_name))


class TotalPriceDisplayFilter(_ContextFilter):
    def __call__(self, context, source, include_taxes=None):
        """
        :type source: shuup.core.order_creator.OrderSource|
                      shuup.core.models.Order
        """
        options = PriceDisplayOptions.from_context(context)
        if options.hide_prices:
            return ""
        if include_taxes is None:
            include_taxes = options.include_taxes
        try:
            if include_taxes is None:
                total = source.total_price
            elif include_taxes:
                total = source.taxful_total_price
            else:
                total = source.taxless_total_price
        except TypeError:
            total = source.total_price
        return money(total)


def get_priced_children_for_price_range(request, product, quantity, supplier):
    catalog = ProductCatalog(
        ProductCatalogContext(
            shop=request.shop,
            user=getattr(request, "user", None),
            supplier=supplier,
            contact=getattr(request, "customer", None),
            purchasable_only=True,
        )
    )

    product_queryset = (
        catalog.get_products_queryset()
        .filter(pk__in=product.variation_children.values_list("pk", flat=True))
        .order_by("catalog_price")
    )

    low = product_queryset.first()

    if low is None:
        return []

    high = product_queryset.last()

    return [
        (low, _get_item_price_info(request, low, quantity, supplier)),
        (high, _get_item_price_info(request, high, quantity, supplier)),
    ]


class PriceRangeDisplayFilter(_ContextFilter):
    def __call__(self, context, product, quantity=1, allow_cache=True, supplier=None):
        """
        :type product: shuup.core.models.Product
        """
        options = PriceDisplayOptions.from_context(context)
        if options.hide_prices:
            return ("", "")

        request = context.get("request")
        priced_products = (
            get_many_cached_price_info(
                request,
                product,
                quantity,
                include_taxes=options.include_taxes,
                supplier=supplier,
            )
            if allow_cache
            else None
        )

        if priced_products is None:
            priced_children_key = PRICED_CHILDREN_CACHE_KEY % (product.id, quantity)
            priced_products = []

            if hasattr(request, priced_children_key):
                priced_children = getattr(request, priced_children_key)
            else:
                priced_children = get_priced_children_for_price_range(request, product, quantity, supplier) or [
                    (
                        product,
                        _get_item_price_info(request, product, quantity, supplier),
                    )
                ]
                setattr(request, priced_children_key, priced_children)

            for child_product, price_info in priced_children:
                if not price_info:
                    continue

                priceful = convert_taxness(request, child_product, price_info, options.include_taxes)
                priced_products.append(priceful)

            if priced_products and allow_cache:
                cache_many_price_info(
                    request,
                    product,
                    quantity,
                    priced_products,
                    include_taxes=options.include_taxes,
                    supplier=supplier,
                )

        if not priced_products:
            return ("", "")

        return (money(priced_products[0].price), money(priced_products[-1].price))


def _get_priceful(request, item, quantity, supplier):
    """
    Get priceful from given item.

    If item has `get_price_info` method, it will be called with given
    `request` and `quantity` as arguments, otherwise the item itself
    should implement the `Priceful` interface.

    :type request: django.http.HttpRequest
    :param request: used as pricing context
    :type item: shuup.core.taxing.TaxableItem
    :type quantity: numbers.Number
    :type supplier: shuup.core.models.Supplier
    :param supplier: used to pass for pricing context
    :rtype: shuup.core.pricing.Priceful|None
    """
    if supplier:
        # Passed from template and sometimes chosen by end user,
        # but most of the time just decided by supplier strategy.
        request.supplier = supplier

    if hasattr(item, "supplier"):
        # When item already has supplier fe. order and basket lines.
        # This is always forced and supplier passed from template
        # can't override this. Though developer should never pass
        # supplier to template filter while getting price for source line.
        request.supplier = item.supplier

    if hasattr(item, "get_price_info"):
        key_prefix = f"{item.id}-{quantity}-"
        if supplier:
            key_prefix += f"-{supplier.id}"

        price_key = f"{key_prefix}_get_priceful"
        if hasattr(request, price_key):
            return getattr(request, price_key)

        price = item.get_price_info(request, quantity=quantity)
        setattr(request, price_key, price)
        return price

    if hasattr(item, "get_total_cost"):
        return item.get_total_cost(request.basket)

    assert isinstance(item, Priceful)
    return item
