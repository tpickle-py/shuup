from typing import Any, Optional, Type

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from shuup.admin.form_part import FormPart, TemplatedFormDef
from shuup.admin.shop_provider import get_shop
from shuup.campaigns.admin_module.forms import BasketCampaignForm, CatalogCampaignForm
from shuup.campaigns.models import ContactGroupSalesRange

from .form_sets import (
    BasketConditionsFormSet,
    BasketDiscountEffectsFormSet,
    BasketLineEffectsFormSet,
    CatalogConditionsFormSet,
    CatalogEffectsFormSet,
    CatalogFiltersFormSet,
)


class SalesRangesForm(forms.ModelForm):
    class Meta:
        model = ContactGroupSalesRange
        fields = ["min_value", "max_value"]
        labels = {"min_value": _("Minimum value"), "max_value": _("Maximum value")}
        help_texts = {"max_value": _("Leave empty for no maximum")}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class SalesRangesFormPart(FormPart):
    priority = 3
    name = "contact_group_sales_ranges"
    form = SalesRangesForm

    def __init__(self, request, **kwargs):
        super().__init__(request, **kwargs)
        self.shops = [get_shop(request)]

    def _get_form_name(self, shop):
        return f"{shop.pk}-{self.name}"

    def get_form_defs(self):
        if not self.object.pk or self.object.is_protected:  # type: ignore
            return

        for shop in self.shops:
            instance, _ = ContactGroupSalesRange.objects.get_or_create(group=self.object, shop=shop)
            yield TemplatedFormDef(
                name=self._get_form_name(shop),
                form_class=self.form,
                template_name="shuup/campaigns/admin/sales_ranges_form_part.jinja",
                required=False,
                kwargs={"instance": instance},
            )

    def form_valid(self, form):
        form_names = [self._get_form_name(shop) for shop in self.shops]
        form_list = [form.forms[name] for name in form_names if name in form.forms]
        for f in form_list:
            if f.changed_data:
                f.save()


class CampaignBaseFormPart(FormPart):
    priority = -1000  # Show this first
    form: Optional[Type[Any]] = None  # Override in subclass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_form_defs(self):
        yield TemplatedFormDef(
            "base",
            self.form,
            required=True,
            template_name="shuup/campaigns/admin/_edit_base_form.jinja",
            kwargs={
                "instance": self.object,
                "languages": settings.LANGUAGES,
                "request": self.request,
            },
        )

    def form_valid(self, form):
        self.object = form["base"].save()
        return self.object


class CatalogBaseFormPart(CampaignBaseFormPart):
    form = CatalogCampaignForm


class BasketBaseFormPart(CampaignBaseFormPart):
    form = BasketCampaignForm


class BaseFormPart(FormPart):
    formset: Optional[Type[Any]] = None
    template_name = "shuup/campaigns/admin/_edit_form.jinja"

    def __init__(self, request, form, name, owner):
        self.name = name
        self.form = form
        super().__init__(request, object=owner)

    def get_form_defs(self):
        yield TemplatedFormDef(
            self.name,
            self.formset,
            self.template_name,
            required=False,
            kwargs={"form": self.form, "owner": self.object},
        )

    def form_valid(self, form):
        component_form = form.forms[self.name]
        component_form.save()

        for component in component_form.new_objects:
            if self.name.startswith("conditions"):
                self.object.conditions.add(component)  # type: ignore
            elif self.name.startswith("filters"):
                self.object.filters.add(component)  # type: ignore


class BasketConditionsFormPart(BaseFormPart):
    formset = BasketConditionsFormSet


class BasketDiscountEffectsFormPart(BaseFormPart):
    formset = BasketDiscountEffectsFormSet


class BasketLineEffectsFormPart(BaseFormPart):
    formset = BasketLineEffectsFormSet


class CatalogConditionsFormPart(BaseFormPart):
    formset = CatalogConditionsFormSet


class CatalogFiltersFormPart(BaseFormPart):
    formset = CatalogFiltersFormSet


class CatalogEffectsFormPart(BaseFormPart):
    formset = CatalogEffectsFormSet
