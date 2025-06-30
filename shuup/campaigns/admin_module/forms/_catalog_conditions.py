from shuup.admin.forms.fields import WeekdayField
from shuup.admin.forms.widgets import TimeInput
from shuup.campaigns.models.context_conditions import ContactCondition, ContactGroupCondition, HourCondition

from ._base import BaseRuleModelForm


class ContactGroupConditionForm(BaseRuleModelForm):
    class Meta(BaseRuleModelForm.Meta):
        model = ContactGroupCondition


class ContactConditionForm(BaseRuleModelForm):
    class Meta(BaseRuleModelForm.Meta):
        model = ContactCondition


class HourConditionForm(BaseRuleModelForm):
    days = WeekdayField()

    class Meta(BaseRuleModelForm.Meta):
        model = HourCondition
        widgets = {
            "hour_start": TimeInput(),
            "hour_end": TimeInput(),
        }
