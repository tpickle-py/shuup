from typing import Any, Optional, Type

from django import forms
from django.db.models import ManyToManyField
from django.utils.translation import gettext_lazy as _

from shuup.admin.forms import ShuupAdminForm
from shuup.admin.forms.fields import ObjectSelect2MultipleField
from shuup.admin.forms.widgets import QuickAddRelatedObjectSelect
from shuup.admin.shop_provider import get_shop
from shuup.utils.django_compat import reverse_lazy


class BaseCampaignForm(ShuupAdminForm):
    class Meta:
        model: Optional[Type[Any]] = None
        exclude = ["identifier", "created_by", "modified_by", "conditions"]

    def __init__(self, **kwargs):
        self.request = kwargs.pop("request")
        self.instance = kwargs.get("instance")
        super().__init__(**kwargs)
        self.fields["shop"].widget = forms.HiddenInput()
        self.fields["shop"].required = False

    @property
    def service_provider(self):
        return getattr(self.instance, self.service_provider_attr) if self.instance else None

    @service_provider.setter
    def service_provider(self, value):
        setattr(self.instance, self.service_provider_attr, value)

    def clean_shop(self):
        return get_shop(self.request)

    def clean(self):
        data = super().clean()

        start_datetime = data.get("start_datetime")
        end_datetime = data.get("end_datetime")
        if start_datetime and end_datetime and end_datetime < start_datetime:
            self.add_error("end_datetime", _("Campaign end date can't be before a start date."))


class CampaignsSelectMultipleField(ObjectSelect2MultipleField):
    def __init__(self, campaign_model, field, *args, **kwargs):
        field_count = len(
            [f for f in campaign_model._meta.get_fields(include_parents=False) if isinstance(f, ManyToManyField)]
        )
        label = field.verbose_name if field_count > 1 else campaign_model.name
        help_text = field.help_text if field_count > 1 else campaign_model().description
        super().__init__(
            *args,
            model=campaign_model,
            label=label,
            help_text=help_text,
            **kwargs,
        )


class BaseEffectModelForm(forms.ModelForm):
    class Meta:
        exclude = ["identifier", "active"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["campaign"].widget = forms.HiddenInput()
        _process_fields(self, **kwargs)


class BaseRuleModelForm(forms.ModelForm):
    class Meta:
        exclude = ["identifier", "active"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        _process_fields(self, **kwargs)


def _process_fields(form, **kwargs):
    instance = kwargs.get("instance")
    model_obj = form._meta.model
    for field in model_obj._meta.get_fields(include_parents=False):
        if not isinstance(field, ManyToManyField):
            continue

        formfield = CampaignsSelectMultipleField(model_obj, field)
        objects = getattr(instance, field.name).all() if instance else model_obj.model.objects.none()
        formfield.required = False
        formfield.initial = objects
        formfield.widget.choices = [(obj.pk, obj.name) for obj in objects]
        form.fields[field.name] = formfield


class QuickAddCouponSelect(QuickAddRelatedObjectSelect):
    url = reverse_lazy("shuup_admin:coupon.new")
