from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext

from shuup.utils.django_compat import force_text


class RelaxedModelChoiceField(forms.ModelChoiceField):
    # `RelaxedModelChoiceField`s allow manually setting `choices` with full validation
    # as an improvement over the normal `ModelChoiceField`.
    def to_python(self, value):
        try:
            return super().to_python(value)
        except ValidationError as verr:
            if verr.code == "invalid_choice":
                # If the original code declared this as invalid, see if we have custom choices.
                if hasattr(self, "_choices"):
                    # Stringly [sic] typed comparison...
                    value = force_text(value)
                    key = self.to_field_name or "pk"
                    for pk, obj in self._choices:
                        if force_text(pk) == value or force_text(getattr(obj, key, "")) == value:
                            if obj is None or isinstance(obj, self.queryset.model):
                                return obj
            raise verr  # Just reraise the original exception then, but from here for clarity


class TypedMultipleChoiceWithLimitField(forms.TypedMultipleChoiceField):
    def __init__(self, min_limit=None, max_limit=None, **kwargs):
        self.min_limit = min_limit
        self.max_limit = max_limit
        super().__init__(**kwargs)

    def clean(self, value):
        value = super().clean(value)
        if self.min_limit is not None and len(value) < self.min_limit:
            error_message = ngettext(
                "You can't select less than {min_limit} item.",
                "You can't select less than {min_limit} items.",
                self.min_limit,
            )
            raise forms.ValidationError(error_message.format(min_limit=self.min_limit))
        if self.max_limit is not None and len(value) > self.max_limit:
            error_message = ngettext(
                "You can't select more than {max_limit} item.",
                "You can't select more than {max_limit} items.",
                self.max_limit,
            )
            raise forms.ValidationError(error_message.format(max_limit=self.max_limit))
        return value
