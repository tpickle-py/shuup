from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from shuup.admin.shop_provider import get_shop
from shuup.discounts.models import Discount
from shuup.utils.django_compat import reverse


class DiscountDeleteView(DetailView):
    model = Discount

    def get_queryset(self):
        return Discount.objects.filter(shop=get_shop(self.request))

    def post(self, request, *args, **kwargs):
        discount = self.get_object()
        discount.delete()
        messages.success(request, _("%s has been deleted.") % discount)
        return HttpResponseRedirect(reverse("shuup_admin:discounts.list"))
