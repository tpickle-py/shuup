from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from shuup.admin.utils.urls import get_model_url
from shuup.core.models import ProductType
from shuup.utils.django_compat import reverse


class ProductTypeDeleteView(DetailView):
    model = ProductType
    context_object_name = "product_type"

    def get(self, request, *args, **kwargs):
        product = self.get_object().product
        return HttpResponseRedirect(get_model_url(product, shop=self.request.shop))

    def post(self, request, *args, **kwargs):
        product_type = self.get_object()
        product_type_repr = str(product_type)
        for product in product_type.products.all().iterator():
            product.type = None
            product.save(update_fields=["type"])
        product_type.delete()
        messages.success(request, _("%s has been marked deleted.") % product_type_repr)
        return HttpResponseRedirect(reverse("shuup_admin:product_type.list"))
