from django.utils.translation import gettext_lazy as _

from shuup.admin.shop_provider import get_shop
from shuup.discounts.models import Discount
from shuup.utils.django_compat import reverse

from ._active_list import DiscountListView


class ArchivedDiscountListView(DiscountListView):
    mass_actions = [
        "shuup.discounts.admin.mass_actions:UnarchiveMassAction",
        "shuup.discounts.admin.mass_actions:DeleteMassAction",
    ]

    def get_queryset(self):
        return Discount.objects.archived(get_shop(self.request))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Archived Product Discounts")
        return context

    def get_object_url(self, instance):
        return reverse("shuup_admin:discounts.edit", kwargs={"pk": instance.pk})
