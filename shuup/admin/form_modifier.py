from django.contrib import messages
from django.db.transaction import atomic

from shuup.apps.provides import get_provide_objects
from shuup.utils.excs import Problem


class ModifiableFormMixin:
    form_modifier_provide_key = None

    def clean(self):
        cleaned_data = super().clean()
        for extend_class in get_provide_objects(self.form_modifier_provide_key):
            extend_class().clean_hook(self)
        return cleaned_data


class ModifiableViewMixin:
    def add_extra_fields(self, form, object=None):
        for extend_class in get_provide_objects(form.form_modifier_provide_key):
            for field_key, field in extend_class().get_extra_fields(object) or []:
                form.fields[field_key] = field

    def get_form(self, form_class=None):
        form = super().get_form(self.form_class)
        self.add_extra_fields(form, self.object)
        return form

    def form_valid_hook(self, form, object):
        has_extension_errors = False
        for extend_class in get_provide_objects(form.form_modifier_provide_key):
            try:
                extend_class().form_valid_hook(form, object)
            except Problem as problem:
                has_extension_errors = True
                messages.error(self.request, problem)
        return has_extension_errors

    @atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        has_extension_errors = self.form_valid_hook(form, self.object)

        if has_extension_errors:
            return self.form_invalid(form)
        else:
            return response


class FormModifier:
    """Base class for form modifiers."""

    def get_extra_fields(self, object=None):
        """Get extra fields to add to the form."""
        return []

    def clean_hook(self, form):
        """Hook for additional form cleaning."""
        pass

    def form_valid_hook(self, form, object):
        """Hook called when form is valid."""
        pass
