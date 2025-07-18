from collections import defaultdict

import bleach
from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import BaseModelFormSet
from django.forms.formsets import DEFAULT_MAX_NUM, DEFAULT_MIN_NUM
from django.utils.translation import gettext_lazy as _
from filer.models import Image

from shuup.admin.forms.fields import ObjectSelect2ModelField, ObjectSelect2ModelMultipleField
from shuup.admin.forms.quick_select import NoModel
from shuup.admin.forms.widgets import (
    FileDnDUploaderWidget,
    QuickAddCategoryMultiSelect,
    QuickAddCategorySelect,
    QuickAddDisplayUnitSelect,
    QuickAddManufacturerSelect,
    QuickAddPaymentMethodsSelect,
    QuickAddProductTypeSelect,
    QuickAddSalesUnitSelect,
    QuickAddShippingMethodsSelect,
    QuickAddSupplierMultiSelect,
    QuickAddTaxClassSelect,
    TextEditorWidget,
)
from shuup.admin.shop_provider import get_shop
from shuup.admin.signals import form_post_clean, form_pre_clean
from shuup.core.models import (
    Attribute,
    AttributeType,
    Category,
    Manufacturer,
    PaymentMethod,
    Product,
    ProductMedia,
    ProductMediaKind,
    ProductType,
    ShippingMethod,
    ShopProduct,
    Supplier,
)
from shuup.utils.i18n import get_language_name
from shuup.utils.multilanguage_model_form import MultiLanguageModelForm, to_language_codes


class ProductBaseForm(MultiLanguageModelForm):
    file = forms.CharField(
        label=_("Primary Product Image"),
        widget=FileDnDUploaderWidget(kind="images", upload_path="/products/images"),
        help_text=_("The main product image. You can add additional images in the `Product Images` tab."),
        required=False,
    )

    class Meta:
        model = Product
        fields = (
            "accounting_identifier",
            "barcode",
            "cost_center",
            "depth",
            "gross_weight",
            "gtin",
            "height",
            "manufacturer",
            "net_weight",
            "profit_center",
            "sales_unit",
            "shipping_mode",
            "sku",
            "tax_class",
            "type",
            "width",
            # I18n
            "description",
            "short_description",
            "keywords",
            "name",
            "slug",
            "variation_name",
        )
        widgets = {
            "keywords": forms.TextInput(),
            "sales_unit": QuickAddSalesUnitSelect(editable_model="shuup.SalesUnit"),
            "tax_class": QuickAddTaxClassSelect(editable_model="shuup.TaxClass"),
            "description": (
                TextEditorWidget()
                if settings.SHUUP_ADMIN_ALLOW_HTML_IN_PRODUCT_DESCRIPTION
                else forms.Textarea(attrs={"rows": 5})
            ),
            "short_description": forms.TextInput(),
        }

    def __init__(self, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(**kwargs)
        self.fields["sales_unit"].required = True  # TODO: Move this to model
        self.fields["type"].required = True
        if self.instance.pk:
            del self.fields["file"]

        self.fields["manufacturer"] = ObjectSelect2ModelField(
            required=False,
            initial=(self.instance.manufacturer if self.instance.pk else None),
            model=Manufacturer,
            widget=QuickAddManufacturerSelect(
                initial=(self.instance.manufacturer if self.instance.pk else None),
                editable_model="shuup.Manufacturer",
                attrs={"data-placeholder": _("Select a manufacturer")},
            ),
        )
        if self.instance.pk:
            initial_type = self.instance.type
        else:
            initial_type = kwargs.get("initial", {}).get("type")

        self.fields["type"] = ObjectSelect2ModelField(
            label=_("Product type"),
            initial=initial_type,
            model=ProductType,
            widget=QuickAddProductTypeSelect(editable_model="shuup.ProductType", initial=initial_type),
        )

    def save(self, **kwargs):
        instance = super().save()
        if self.cleaned_data.get("file") and instance.primary_image is None:
            image = ProductMedia.objects.create(
                product=instance,
                file_id=self.cleaned_data["file"],
                kind=ProductMediaKind.IMAGE,
            )
            shop = self.request.shop
            image.shops.add(shop)
            instance.primary_image = image
            instance.save()
        return instance

    def clean(self):
        form_pre_clean.send(Product, instance=self.instance, cleaned_data=self.cleaned_data)
        super().clean()

        if not settings.SHUUP_ADMIN_ALLOW_HTML_IN_PRODUCT_DESCRIPTION:
            for key, value in self.cleaned_data.items():
                if key.startswith("description__"):
                    self.cleaned_data[key] = bleach.clean(value, tags=[])

        form_post_clean.send(Product, instance=self.instance, cleaned_data=self.cleaned_data)


class ShopProductForm(MultiLanguageModelForm):
    class Meta:
        model = ShopProduct
        fields = (
            "default_price_value",
            "minimum_price_value",
            "suppliers",
            "available_until",
            "visibility",
            "purchasable",
            "visibility_limit",
            "visibility_groups",
            "purchase_multiple",
            "minimum_purchase_quantity",
            "backorder_maximum",
            "display_unit",
            "limit_shipping_methods",
            "limit_payment_methods",
            "shipping_methods",
            "payment_methods",
            "primary_category",
            "categories",
            # i18n
            "status_text",
            # TODO: "shop_primary_image",
        )
        help_texts = {
            "backorder_maximum": _(
                "Number of units that can be purchased after the product is out of stock. "
                "Set to blank for product to be purchasable without limits."
            )
        }
        widgets = {
            "display_unit": QuickAddDisplayUnitSelect(editable_model="shuup.DisplayUnit"),
            "payment_methods": QuickAddPaymentMethodsSelect(),
            "shipping_methods": QuickAddShippingMethodsSelect(),
        }

    def __init__(self, **kwargs):
        # TODO: Revise this. Since this is shop product form then maybe we should have shop available insted of request
        self.request = kwargs.pop("request", None)
        super().__init__(**kwargs)

        if "default_price_value" in self.fields:
            self.initial["default_price_value"] = self.initial["default_price_value"] or 0

        payment_methods_qs = PaymentMethod.objects.all()
        shipping_methods_qs = ShippingMethod.objects.all()
        if self.request:
            shop = self.request.shop
            payment_methods_qs = payment_methods_qs.filter(shop=shop)
            shipping_methods_qs = ShippingMethod.objects.filter(shop=shop)
        self.fields["payment_methods"].queryset = payment_methods_qs  # type: ignore
        self.fields["shipping_methods"].queryset = shipping_methods_qs  # type: ignore
        self.fields["default_price_value"].required = True

        initial_categories = []
        initial_suppliers = []

        if self.instance.pk:
            initial_categories = self.instance.categories.all()
            initial_suppliers = self.instance.suppliers.all()
        elif not settings.SHUUP_ENABLE_MULTIPLE_SUPPLIERS:
            supplier = Supplier.objects.first()
            initial_suppliers = [supplier] if supplier else []

        if settings.SHUUP_ADMIN_LOAD_SELECT_OBJECTS_ASYNC.get("suppliers"):
            self.fields["suppliers"] = ObjectSelect2ModelMultipleField(
                initial=initial_suppliers,
                model=Supplier,
                widget=QuickAddSupplierMultiSelect(initial=initial_suppliers, attrs={"data-search-mode": "enabled"}),
                label=self.fields["suppliers"].label,
                required=False,
            )
        else:
            self.fields["suppliers"].widget = QuickAddSupplierMultiSelect(initial=initial_suppliers)

        if settings.SHUUP_ADMIN_LOAD_SELECT_OBJECTS_ASYNC.get("categories"):
            self.fields["primary_category"] = ObjectSelect2ModelField(
                initial=(self.instance.primary_category if self.instance.pk else None),
                model=Category,
                widget=QuickAddCategorySelect(
                    editable_model="shuup.Category",
                    initial=(self.instance.primary_category if self.instance.pk else None),
                    attrs={"data-placeholder": _("Select a category")},
                ),
                label=self.fields["primary_category"].label,
                required=False,
            )
            self.fields["categories"] = ObjectSelect2ModelMultipleField(
                initial=initial_categories,
                model=Category,
                widget=QuickAddCategoryMultiSelect(initial=initial_categories),
                label=self.fields["categories"].label,
                required=False,
            )
        else:
            categories_choices = [
                (cat.pk, cat.get_hierarchy())
                for cat in Category.objects.filter(shop=get_shop(self.request)).exclude(deleted=True)
            ]
            self.fields["primary_category"].widget = QuickAddCategorySelect(
                initial=(
                    self.instance.primary_category if self.instance.pk and self.instance.primary_category else None
                ),
                editable_model="shuup.Category",
                attrs={"data-placeholder": _("Select a category")},
                choices=categories_choices,
                model=NoModel(),
            )
            self.fields["categories"].widget = QuickAddCategoryMultiSelect(
                initial=initial_categories, choices=categories_choices, model=NoModel()
            )

    def clean(self):
        form_pre_clean.send(ShopProduct, instance=self.instance, cleaned_data=self.cleaned_data)
        data = super().clean()
        if not getattr(settings, "SHUUP_AUTO_SHOP_PRODUCT_CATEGORIES", False):
            return data

        # handle this here since form_part save causes problems with signals
        primary_category = data.get("primary_category")
        categories = data.get("categories", []) or []
        if categories:
            categories = list(categories)

        if not primary_category and categories:
            primary_category = categories[0]  # first is going to be primary

        if primary_category and primary_category not in categories:
            combined = [primary_category] + categories
            categories = combined

        data["primary_category"] = primary_category
        data["categories"] = categories

        form_post_clean.send(ShopProduct, instance=self.instance, cleaned_data=data)
        return data


class ProductAttributesForm(forms.Form):
    def __init__(self, **kwargs):
        self.default_language = kwargs.pop("default_language", settings.PARLER_DEFAULT_LANGUAGE_CODE)
        self.languages = to_language_codes(kwargs.pop("languages", ()), self.default_language)
        self.language_names = {lang: get_language_name(lang) for lang in self.languages}
        self.product = kwargs.pop("product")
        self.attributes = self.product.get_available_attribute_queryset()
        self.trans_name_map = defaultdict(dict)
        self.translated_field_names = []
        super().__init__(**kwargs)
        self.applied_attrs = self._get_applied_attributes()
        self._field_languages = {}
        self._build_fields()
        self.empty_permitted = False

    def _get_applied_attributes(self):
        applied_attrs = {}
        if self.product.pk:
            for pa in self.product.attributes.select_related("attribute").prefetch_related("chosen_options"):
                applied_attrs[pa.attribute_id] = pa
        return applied_attrs

    def _build_fields(self):
        for attribute in self.attributes:
            self._field_languages[attribute.identifier] = {}
            pa = self.applied_attrs.get(attribute.pk)
            if attribute.type == AttributeType.TRANSLATED_STRING:
                self._process_multilang_attr(attribute, pa)
            else:
                self.fields[attribute.identifier] = attribute.formfield()
                if pa:
                    if attribute.type == AttributeType.TIMEDELTA:  # Special case.
                        value = pa.numeric_value
                    elif attribute.type == AttributeType.CHOICES:
                        value = [choice.id for choice in pa.chosen_options.all()]
                    else:
                        value = pa.value
                    self.initial[attribute.identifier] = value
                self._field_languages[attribute.identifier][None] = attribute.identifier

    def _process_multilang_attr(self, attribute, pa):
        languages = tuple(self.languages)
        if pa:  # Ensure the fields for languages in the database but not currently otherwise available are visible
            extant_languages = pa.get_available_languages()
            languages += tuple(lang for lang in extant_languages if lang not in languages)
        else:
            extant_languages = set()
        for lang in languages:
            field_name = f"{attribute.identifier}__{lang}"
            self.fields[field_name] = field = attribute.formfield()
            field.label = f"{field.label} [{get_language_name(lang)}]"
            self.trans_name_map[lang][field_name] = field_name
            self.translated_field_names.append(field_name)

            if pa and lang in extant_languages:
                self.initial[field_name] = getattr(pa.get_translation(lang), "translated_string_value", None)
            self._field_languages[attribute.identifier][lang] = field_name

    def save(self):
        if not self.has_changed():  # Nothing to do, don't bother iterating
            return
        for attribute in self.attributes:
            for language, field_name in self._field_languages[attribute.identifier].items():
                if field_name not in self.cleaned_data:
                    continue
                value = self.cleaned_data[field_name]
                if attribute.is_translated and not value:
                    value = ""
                try:
                    self.product.set_attribute_value(attribute.identifier, value, language)
                except Attribute.DoesNotExist:
                    # This may occur when the user changes a product type (the attribute is no longer in
                    # `product.get_available_attribute_queryset()`. In this case, we just drop the assignment.
                    # TODO: Should we maybe _not_ drop the assignment?
                    pass
        self.product.clear_attribute_cache()


class BaseProductMediaForm(MultiLanguageModelForm):
    class Meta:
        model = ProductMedia
        fields = (
            "file",
            "ordering",
            "external_url",
            "public",
            "title",
            "description",
            "purchased",
            "kind",
        )

    def __init__(self, **kwargs):
        self.product = kwargs.pop("product")
        self.allowed_media_kinds = kwargs.pop("allowed_media_kinds")
        super().__init__(**kwargs)

        self.fields["file"].widget = forms.HiddenInput()
        self.fields["file"].required = True

        if self.allowed_media_kinds:
            # multiple media kinds allowed, filter the choices list to reflect the `self.allowed_media_kinds`
            allowed_kinds_values = {v.value for v in self.allowed_media_kinds}
            self.filter_allowed_kinds(allowed_kinds_values)

            if len(self.allowed_media_kinds) == 1:
                # only one media kind given, no point showing the dropdown
                self.fields["kind"].widget = forms.HiddenInput()

            self.fields["kind"].initial = self.allowed_media_kinds[0]

        self.file_url = self.instance.url

    def filter_allowed_kinds(self, allowed_kinds_values):
        if "kind" not in self.fields:
            return []
        if not self.fields["kind"].choices:
            return []
        self.fields["kind"].choices = [
            (value, choice) for value, choice in self.fields["kind"].choices if value in allowed_kinds_values
        ]

    def get_thumbnail(self, request):
        """
        Get thumbnail url.

        If thumbnail creation fails for whatever reason,
        an error message is displayed for user.
        """
        try:
            thumbnail = self.instance.get_thumbnail()
        except (OSError, ValueError) as error:
            msg = _("Thumbnail generation of %(media)s failed: %(error)s.") % {
                "media": self.instance,
                "error": error,
            }
            messages.error(request, msg)
            thumbnail = None
        return thumbnail

    def pre_master_save(self, instance):
        instance.product = self.product
        shop = self.request.shop
        instance.shops.add(shop)


class BaseProductMediaFormSet(BaseModelFormSet):
    validate_min = False
    min_num = DEFAULT_MIN_NUM
    validate_max = False
    max_num = DEFAULT_MAX_NUM
    absolute_max = DEFAULT_MAX_NUM
    model = ProductMedia
    can_delete = True
    can_order = False
    extra = 0

    allowed_media_kinds = []
    form_class = BaseProductMediaForm

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop("product")
        self.request = kwargs.pop("request", None)
        self.default_language = kwargs.pop("default_language", settings.PARLER_DEFAULT_LANGUAGE_CODE)
        self.languages = to_language_codes(kwargs.pop("languages", ()), self.default_language)
        kwargs.pop("empty_permitted", None)  # this is unknown to formset
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        qs = ProductMedia.objects.filter(product=self.product)
        if self.allowed_media_kinds:
            qs = qs.filter(kind__in=self.allowed_media_kinds)
        return qs.distinct()

    def form(self, **kwargs):
        kwargs.setdefault("languages", self.languages)
        kwargs.setdefault("product", self.product)
        kwargs.setdefault("allowed_media_kinds", self.allowed_media_kinds)
        return self.form_class(**kwargs)

    def save(self, commit=True):
        form_list = self.forms or []
        for i, form in enumerate(form_list):
            if hasattr(form, "request"):
                continue
            form_list[i] = form.__class__(**{**form.initial, "request": self.request, "instance": form.instance})
        super().save(commit)

    @property
    def empty_form(self):
        # Use the documented approach: pass total_form_count() to _construct_form
        form = self._construct_form(self.total_form_count())
        form.empty_permitted = True
        return form

    @property
    def can_delete_extra(self):
        return False


class ProductMediaForm(BaseProductMediaForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["file"].required = False

    def clean_external_url(self):
        external_url = self.cleaned_data.get("external_url")

        # if form has been deleted, we don't want to validate fields
        if "DELETE" in self.changed_data:
            return external_url

        file = self.cleaned_data.get("file")
        if external_url and file:
            raise ValidationError(_("Use only URL or file, not both."))
        return external_url


class ProductMediaFormSet(BaseProductMediaFormSet):
    form_class = ProductMediaForm
    allowed_media_kinds = [
        ProductMediaKind.GENERIC_FILE,
        ProductMediaKind.DOCUMENTATION,
        ProductMediaKind.SAMPLE,
    ]


class ProductImageMediaForm(BaseProductMediaForm):
    is_primary = forms.BooleanField(required=False, label=_("Is primary"))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["file"].widget = forms.HiddenInput()

        if self.instance.pk and self.instance.file:
            if self.product.primary_image_id == self.instance.pk:
                self.fields["is_primary"].initial = True

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file and not isinstance(file, Image):
            raise ValidationError(_("Only images are allowed in this field."))
        return file

    def save(self, commit=True):
        instance = super().save(commit)
        if self.cleaned_data.get("is_primary"):
            self.product.primary_image = instance
            self.product.save()
        return instance


class ProductImageMediaFormSet(ProductMediaFormSet):
    allowed_media_kinds = [ProductMediaKind.IMAGE]
    form_class = ProductImageMediaForm

    def save(self, commit=True):
        """
        Save the form.

        In addition add the first saved image as primary image for the
        product if none is selected as such.
        """
        super().save(commit)
        self.product.refresh_from_db()
        if not self.product.primary_image:
            fallback_primary_image = self.product.media.filter(
                enabled=True, public=True, kind=ProductMediaKind.IMAGE
            ).first()
            Product.objects.filter(id=self.product.pk).update(primary_image=fallback_primary_image)
