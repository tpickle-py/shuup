from django.utils.translation import gettext_lazy as _

from shuup.admin.forms.fields import PercentageField
from shuup.campaigns.models.product_effects import ProductDiscountAmount, ProductDiscountPercentage

from ._base import BaseEffectModelForm

COMMON_EXCLUDES = ["identifier", "active"]


class ProductDiscountAmountForm(BaseEffectModelForm):
    class Meta(BaseEffectModelForm.Meta):
        model = ProductDiscountAmount
        exclude = COMMON_EXCLUDES


class ProductDiscountPercentageForm(BaseEffectModelForm):
    discount_percentage = PercentageField(
        max_digits=6,
        decimal_places=5,
        label=_("discount percentage"),
        help_text=_("The discount percentage for this campaign."),
    )

    class Meta(BaseEffectModelForm.Meta):
        model = ProductDiscountPercentage
        exclude = COMMON_EXCLUDES
