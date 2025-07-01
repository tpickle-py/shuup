from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView

from shuup.admin.utils.urls import get_model_url
from shuup.core.models import Category
from shuup.utils.django_compat import reverse


class CategoryDeleteView(DetailView):
    model = Category
    context_object_name = "category"

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(get_model_url(self.get_object()))

    def post(self, request, *args, **kwargs):
        category = self.get_object()
        category.soft_delete()
        messages.success(request, _("%s has been deleted.") % category)
        return HttpResponseRedirect(reverse("shuup_admin:category.list"))
