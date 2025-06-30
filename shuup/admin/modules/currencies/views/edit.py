from django import forms

from shuup.admin.utils.views import CreateOrUpdateView
from shuup.core.models import Currency


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        exclude = ()


class CurrencyEditView(CreateOrUpdateView):
    model = Currency
    form_class = CurrencyForm
    template_name = "shuup/admin/currencies/edit_currency.jinja"
    context_object_name = "currency"
    add_form_errors_as_messages = True
