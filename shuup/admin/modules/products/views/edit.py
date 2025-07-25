import bleach
from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import atomic
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from shuup.admin.form_part import FormPart, FormPartsViewMixin, SaveFormPartsMixin, TemplatedFormDef
from shuup.admin.modules.products.forms import (
    ProductAttributesForm,
    ProductBaseForm,
    ProductImageMediaFormSet,
    ProductMediaFormSet,
    ShopProductForm,
)
from shuup.admin.shop_provider import get_shop
from shuup.admin.supplier_provider import get_supplier
from shuup.admin.utils.tour import is_tour_complete
from shuup.admin.utils.views import CreateOrUpdateView
from shuup.apps.provides import get_provide_objects
from shuup.core.models import Product, ProductType, SalesUnit, ShopProduct, Supplier, TaxClass
from shuup.core.specs.product_kind import DefaultProductKindSpec, get_product_kind_specs

from .toolbars import EditProductToolbar


class ProductBaseFormPart(FormPart):
    priority = -1000  # Show this first, no matter what

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            ProductBaseForm,
            template_name="shuup/admin/products/_edit_base_form.jinja",
            required=True,
            kwargs={
                "instance": self.object.product,
                "languages": settings.LANGUAGES,
                "initial": self.get_initial(),
                "request": self.request,
            },
        )

        yield TemplatedFormDef(
            "base_extra",
            forms.Form,
            template_name="shuup/admin/products/_edit_extra_base_form.jinja",
            required=False,
        )

    def form_valid(self, form_group):
        self.object.product = form_group["base"].save()
        self.object.save()
        return self.object.product

    def get_sku(self):
        sku = self.request.GET.get("sku", "")
        if not sku:
            last_id = Product.objects.values_list("id", flat=True).first()
            sku = last_id + 1 if last_id else 1
        return sku

    def get_initial(self):
        if not self.object.product_id:
            # Sane defaults...
            name_field = f"name__{get_language()}"
            return {
                name_field: self.request.GET.get("name", ""),
                "sku": self.get_sku(),
                "type": ProductType.objects.first(),
                "tax_class": TaxClass.objects.first(),
                "sales_unit": SalesUnit.objects.first(),
            }


class ShopProductFormPart(FormPart):
    priority = -900

    def __init__(self, request, **kwargs):
        super().__init__(request, **kwargs)
        self.shop = request.shop

    def get_form_defs(self):
        yield TemplatedFormDef(
            f"shop{self.shop.pk}",
            ShopProductForm,
            template_name="shuup/admin/products/_edit_shop_form.jinja",
            required=True,
            kwargs={
                "instance": self.object,
                "initial": self.get_initial(),
                "request": self.request,
                "languages": settings.LANGUAGES,
            },
        )

        # the hidden extra form template that uses ShopProductForm
        yield TemplatedFormDef(
            f"shop{self.shop.pk}_extra",
            forms.Form,
            template_name="shuup/admin/products/_edit_extra_shop_form.jinja",
            required=False,
        )

    def form_valid(self, form):
        shop_product_form = form[f"shop{self.shop.pk}"]
        if not shop_product_form.changed_data:
            return
        if not shop_product_form.instance.pk:
            shop_product_form.instance.product = self.object

        original_quantity = shop_product_form.instance.minimum_purchase_quantity
        rounded_quantity = self.object.sales_unit.round(original_quantity)  # type: ignore
        if original_quantity != rounded_quantity:
            messages.info(
                self.request,
                _("Minimum Purchase Quantity has been rounded to match Sales Unit."),
            )

        shop_product_form.instance.minimum_purchase_quantity = rounded_quantity
        inst = shop_product_form.save()
        messages.success(self.request, _("Changes to shop instance for %s saved.") % inst.shop)

    def get_initial(self):
        if not self.object.pk:  # type: ignore
            return {"suppliers": [Supplier.objects.enabled(shop=get_shop(self.request)).first()]}  # type: ignore

    def has_perm(self):
        return True  # Right form parts are defined at init


class ProductAttributeFormPart(FormPart):
    priority = -800

    def get_form_defs(self):
        if not self.object.product.get_available_attribute_queryset():  # type: ignore
            return
        yield TemplatedFormDef(
            "attributes",
            ProductAttributesForm,
            template_name="shuup/admin/products/_edit_attribute_form.jinja",
            required=False,
            kwargs={"product": self.object.product, "languages": settings.LANGUAGES},  # type: ignore
        )

    def form_valid(self, form):
        if "attributes" in form.forms:
            form.forms["attributes"].save()


class BaseProductMediaFormPart(FormPart):
    def get_form_defs(self):
        if not self.object.pk:  # type: ignore
            return

        yield TemplatedFormDef(
            self.name,  # type: ignore
            self.formset,  # type: ignore
            template_name="shuup/admin/products/_edit_media_form.jinja",
            required=False,
            kwargs={
                "product": self.object.product,  # type: ignore
                "languages": settings.LANGUAGES,
                "request": self.request,
            },
        )

    def form_valid(self, form):
        if self.name in form.forms:  # type: ignore
            frm = form.forms[self.name]  # type: ignore
            frm.save()


class ProductMediaFormPart(BaseProductMediaFormPart):
    name = "media"
    priority = -700
    formset = ProductMediaFormSet


class ProductImageMediaFormPart(BaseProductMediaFormPart):
    name = "images"
    priority = -600
    formset = ProductImageMediaFormSet


class ProductEditView(SaveFormPartsMixin, FormPartsViewMixin, CreateOrUpdateView):
    model = ShopProduct
    context_object_name = "product"
    template_name = "shuup/admin/products/edit.jinja"
    base_form_part_classes = []
    form_part_class_provide_key = "admin_product_form_part"
    add_form_errors_as_messages = True
    product_listing_names = [DefaultProductKindSpec.admin_listing_name]

    def get_listing_product_kinds_values(self):
        return [
            product_kind_spec.value
            for product_kind_spec in get_product_kind_specs()
            if product_kind_spec.admin_listing_name in self.product_listing_names
        ]

    def get_object(self, queryset=None):
        if not self.kwargs.get(self.pk_url_kwarg):
            instance = self.model()
            instance.shop = self.request.shop
            instance.product = Product()
            return instance
        return super().get_object(queryset)

    @atomic
    def form_valid(self, form):
        return self.save_form_parts(form)

    def get_toolbar(self):
        return EditProductToolbar(view=self)

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .filter(
                shop=get_shop(self.request),
                product__kind__in=self.get_listing_product_kinds_values(),
            )
        )

        supplier = get_supplier(self.request)
        if supplier:
            qs = qs.filter(suppliers=supplier)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orderability_errors = []

        shop = get_shop(self.request)
        if self.object.pk:
            context["title"] = self.object.product.name
            try:
                shop_product = self.object
                orderability_errors.extend(
                    [
                        f"{shop.name}: {msg.message}"
                        for msg in shop_product.get_orderability_errors(
                            supplier=None,
                            quantity=shop_product.minimum_purchase_quantity,
                            customer=None,
                        )
                    ]
                )
            except ObjectDoesNotExist:
                orderability_errors.extend(["Error! {}: {}".format(shop.name, _("Product is not available."))])

            product_validator_provides = sorted(
                get_provide_objects("admin_product_validator"),
                key=lambda provides: provides.ordering,
            )
            context["bleach"] = bleach
            validation_issues = []
            for admin_product_validator in product_validator_provides:
                for validation_issue in admin_product_validator.get_validation_issues(
                    shop_product=self.object,
                    shop=shop,
                    user=self.request.user,
                    supplier=get_supplier(self.request),
                ):
                    if validation_issue:
                        validation_issues.append(validation_issue)
            context["validation_issues"] = sorted(validation_issues, key=lambda x: x.get_issue_type_priority())

        context["orderability_errors"] = orderability_errors
        context["product_sections"] = []
        context["tour_key"] = "product"
        context["tour_complete"] = is_tour_complete(get_shop(self.request), "product", user=self.request.user)

        product_sections_provides = sorted(get_provide_objects("admin_product_section"), key=lambda x: x.order)
        for admin_product_section in product_sections_provides:
            if admin_product_section.visible_for_object(self.object.product, self.request):
                context["product_sections"].append(admin_product_section)
                context[admin_product_section.identifier] = admin_product_section.get_context_data(
                    self.object.product, self.request
                )

        return context
