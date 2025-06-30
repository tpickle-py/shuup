


from shuup.admin.utils.views import CreateOrUpdateView
from shuup.core.models import DisplayUnit, SalesUnit
from shuup.utils.multilanguage_model_form import MultiLanguageModelForm


class SalesUnitForm(MultiLanguageModelForm):
    class Meta:
        model = SalesUnit
        exclude = ()  # All the fields!


class SalesUnitEditView(CreateOrUpdateView):
    model = SalesUnit
    form_class = SalesUnitForm
    template_name = "shuup/admin/sales_units/edit.jinja"
    context_object_name = "sales_unit"


class DisplayUnitForm(MultiLanguageModelForm):
    class Meta:
        model = DisplayUnit
        exclude = ()  # All the fields!


class DisplayUnitEditView(CreateOrUpdateView):
    model = DisplayUnit
    form_class = DisplayUnitForm
    template_name = "shuup/admin/sales_units/edit_display_unit.jinja"
    context_object_name = "display_unit"
