from django.conf import settings
from django.db.models import Q
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from shuup.admin.shop_provider import get_shop
from shuup.admin.supplier_provider import get_supplier
from shuup.admin.utils.picotable import ChoicesFilter, Column, Picotable, RangeFilter, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import ProductMode, ShopProduct
from shuup.core.specs.product_kind import DefaultProductKindSpec, get_product_kind_specs
from shuup.utils.iterables import first


class ProductPicotable(Picotable):
    def process_item(self, object):
        out = super().process_item(object)
        popup = self.request.GET.get("popup")
        kind = self.request.GET.get("kind", "")
        if popup and kind == "product":  # Enable option to pick products
            out.update({"_id": object.product.id})
            out["popup"] = True
        return out


class ProductListView(PicotableListView):
    model = ShopProduct
    picotable_class = ProductPicotable
    product_listing_names = [DefaultProductKindSpec.admin_listing_name]

    default_columns = [
        Column(
            "primary_image",
            _("Primary Image"),
            display="get_primary_image",
            class_name="text-center",
            raw=True,
            ordering=1,
            sortable=False,
        ),
        Column(
            "product_name",
            _("Name"),
            sort_field="product__translations__name",
            display="product__name",
            filter_config=TextFilter(
                filter_field="product__translations__name",
                placeholder=_("Filter by name..."),
            ),
            ordering=2,
        ),
        Column(
            "product_sku",
            _("SKU"),
            display="product__sku",
            filter_config=RangeFilter(filter_field="product__sku"),
            ordering=3,
        ),
        Column(
            "product_barcode",
            _("Barcode"),
            display="product__barcode",
            filter_config=TextFilter(placeholder=_("Filter by barcode...")),
            ordering=4,
        ),
        Column(
            "product_mode",
            _("Mode"),
            display="product__mode",
            filter_config=ChoicesFilter(ProductMode.choices),
            ordering=5,
        ),
        Column(
            "primary_category",
            _("Primary Category"),
            display=(lambda instance: instance.primary_category.name if instance.primary_category else None),
            filter_config=TextFilter(
                filter_field="primary_category__translations__name",
                placeholder=_("Filter by category name..."),
            ),
            ordering=6,
        ),
        Column(
            "categories",
            _("Categories"),
            display="format_categories",
            filter_config=TextFilter(
                filter_field="categories__translations__name",
                placeholder=_("Filter by category name..."),
            ),
            ordering=7,
        ),
    ]

    related_objects = [
        ("product", "shuup.core.models:Product"),
    ]

    mass_actions = [
        "shuup.admin.modules.products.mass_actions:VisibleMassAction",
        "shuup.admin.modules.products.mass_actions:InvisibleMassAction",
        "shuup.admin.modules.products.mass_actions:ExportProductsCSVAction",
        "shuup.admin.modules.products.mass_actions:EditProductAttributesAction",
    ]
    toolbar_buttons_provider_key = "product_list_toolbar_provider"
    mass_actions_provider_key = "product_list_mass_actions_provider"

    def __init__(self):
        def get_suppliers_column(iterable):
            return first(
                [col for col in iterable if col.id in ["suppliers", "shopproduct_suppliers"]],
                default=None,
            )

        def get_suppliers_filter():
            return TextFilter(
                filter_field="suppliers__name",
                placeholder=_("Filter by supplier name..."),
            )

        if settings.SHUUP_ENABLE_MULTIPLE_SUPPLIERS and not get_suppliers_column(self.default_columns):
            self.default_columns.append(
                Column(
                    "suppliers",
                    _("Suppliers"),
                    display="format_suppliers",
                    ordering=8,
                    filter_config=get_suppliers_filter(),
                )
            )
        super().__init__()
        suppliers_column = get_suppliers_column(self.columns)
        if suppliers_column:
            suppliers_column.filter_config = get_suppliers_filter()

    def format_categories(self, instance):
        return ", ".join(category.name for category in instance.categories.all()) or "-"

    def format_suppliers(self, instance):
        return ", ".join(list(instance.suppliers.values_list("name", flat=True)))

    def get_primary_image(self, instance):
        if instance.product.primary_image:
            thumbnail = instance.product.primary_image.get_thumbnail()
            if thumbnail:
                return f"<img src='{thumbnail.url}'>"
        return f"<img src='{static('shuup_admin/img/no_image_thumbnail.png')}'>"

    def get_listing_product_kinds_values(self):
        return [
            product_kind_spec.value
            for product_kind_spec in get_product_kind_specs()
            if product_kind_spec.admin_listing_name in self.product_listing_names
        ]

    def get_queryset(self):
        filter = self.get_filter()
        shop = get_shop(self.request)
        qs = ShopProduct.objects.filter(
            product__deleted=False,
            product__kind__in=self.get_listing_product_kinds_values(),
            shop=shop,
        )
        q = Q()
        for mode in filter.get("modes", []):
            q |= Q(product__mode=mode)
        manufacturer_ids = filter.get("manufacturers")
        if manufacturer_ids:
            q |= Q(product__manufacturer_id__in=manufacturer_ids)
        qs = qs.filter(q)

        supplier = get_supplier(self.request)
        if supplier:
            qs = qs.filter(suppliers=supplier)

        return qs

    def get_object_abstract(self, instance, item):
        return [
            {"text": f"{instance.product}", "class": "header"},
            {"title": _("Barcode"), "text": item.get("product__barcode")},
            {"title": _("SKU"), "text": item.get("product__sku")},
            {"title": _("Type"), "text": item.get("product__type")},
        ]
