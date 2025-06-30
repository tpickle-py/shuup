

from django.forms.formsets import DELETION_FIELD_NAME, BaseFormSet


class ProductChildBaseFormSet(BaseFormSet):
    deletion_label = None

    def __init__(self, **kwargs):
        kwargs.pop("empty_permitted", None)
        self.request = kwargs.pop("request", None)

        super(ProductChildBaseFormSet, self).__init__(**kwargs)

    def _construct_form(self, i, **kwargs):
        form = super(ProductChildBaseFormSet, self)._construct_form(i, **kwargs)
        form.fields[DELETION_FIELD_NAME].label = self.deletion_label
        return form
