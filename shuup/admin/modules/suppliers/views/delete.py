from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from shuup.admin.shop_provider import get_shop
from shuup.admin.supplier_provider import get_supplier
from shuup.core.models import Supplier
from shuup.utils.django_compat import reverse


class SupplierDeleteView(DetailView):
    model = Supplier

    def get_success_url(self):
        return reverse("shuup_admin:supplier.list")

    def get_queryset(self, *args, **kwargs):
        queryset = Supplier.objects.filter(shops=get_shop(self.request)).not_deleted()
        supplier = get_supplier(self.request)
        if supplier:
            # If admin has supplier enabled allow only delete self
            # althought not good view to enable for vendor
            queryset = queryset.filter(id=supplier.pk)
        return queryset

    def post(self, request, *args, **kwargs):
        supplier = self.get_object()
        supplier.soft_delete()
        messages.success(request, _("Success! %s has been marked deleted.") % supplier)
        return HttpResponseRedirect(self.get_success_url())
