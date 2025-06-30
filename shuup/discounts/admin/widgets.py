from shuup.admin.forms.quick_select import QuickAddRelatedObjectMultiSelect
from shuup.utils.django_compat import reverse_lazy


class QuickAddHappyHourMultiSelect(QuickAddRelatedObjectMultiSelect):
    url = reverse_lazy("shuup_admin:discounts_happy_hour.new")
