from django.views.generic import DeleteView

from shuup.core.models import ServiceProvider
from shuup.utils.django_compat import reverse_lazy


class ServiceProviderDeleteView(DeleteView):
    model = ServiceProvider
    success_url = reverse_lazy("shuup_admin:service_provider.list")
