from django.views.generic import DeleteView

from shuup.core.models import ContactGroup
from shuup.utils.django_compat import reverse_lazy


class ContactGroupDeleteView(DeleteView):
    model = ContactGroup
    success_url = reverse_lazy("shuup_admin:contact_group.list")
