

from shuup.admin.modules.contact_group_price_display.views.forms import ContactGroupPriceDisplayForm
from shuup.admin.utils.views import CreateOrUpdateView
from shuup.core.models import ContactGroupPriceDisplay
from shuup.utils.django_compat import reverse_lazy


class ContactGroupPriceDisplayEditView(CreateOrUpdateView):
    model = ContactGroupPriceDisplay
    form_class = ContactGroupPriceDisplayForm
    template_name = "shuup/admin/contact_group_price_display/edit.jinja"
    context_object_name = "price_display"
    add_form_errors_as_messages = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_success_url(self):
        return reverse_lazy("shuup_admin:contact_group_price_display.list")
