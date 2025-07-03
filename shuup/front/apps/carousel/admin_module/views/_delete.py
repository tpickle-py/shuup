from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from shuup.admin.utils.urls import get_model_url
from shuup.front.apps.carousel.models import Carousel
from shuup.utils.django_compat import reverse


class CarouselDeleteView(DetailView):
    model = Carousel
    context_object_name = "carousel"

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(get_model_url(self.get_object()))

    def post(self, request, *args, **kwargs):
        carousel = self.get_object()
        name = carousel.name
        carousel.delete()
        messages.success(request, _("%s has been deleted.") % name)
        return HttpResponseRedirect(reverse("shuup_admin:carousel.list"))
