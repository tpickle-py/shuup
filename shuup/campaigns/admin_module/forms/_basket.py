from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from shuup.admin.shop_provider import get_shop
from shuup.admin.supplier_provider import get_supplier
from shuup.campaigns.models import BasketCampaign, Coupon

from ._base import BaseCampaignForm, QuickAddCouponSelect


class BasketCampaignForm(BaseCampaignForm):
    class Meta(BaseCampaignForm.Meta):
        model = BasketCampaign

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        coupons = Coupon.objects.filter(
            Q(active=True, shop=get_shop(self.request)),
            Q(campaign=None) | Q(campaign=self.instance),
        )
        supplier = get_supplier(self.request)
        if supplier:
            coupons = coupons.filter(supplier=supplier)

        coupon_code_choices = [("", "---------")] + list(coupons.values_list("pk", "code"))
        field_kwargs = {"choices": coupon_code_choices, "required": False}
        field_kwargs["help_text"] = _("Define the required coupon for this campaign.")
        field_kwargs["label"] = _("Coupon")
        field_kwargs["widget"] = QuickAddCouponSelect(editable_model="campaigns.Coupon")
        if self.instance.pk and self.instance.coupon:
            field_kwargs["initial"] = self.instance.coupon.pk

        self.fields["coupon"] = forms.ChoiceField(**field_kwargs)

        # the supplier will be, by default, the current one
        if supplier:
            self.fields["supplier"].widget = forms.HiddenInput()

    def clean_coupon(self):
        coupon = self.cleaned_data.get("coupon")
        if coupon:
            coupon = Coupon.objects.get(pk=coupon)
        return coupon or None

    def clean_supplier(self):
        return self.cleaned_data.get("supplier") or get_supplier(self.request)
