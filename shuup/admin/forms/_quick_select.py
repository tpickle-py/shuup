from django.forms import Select, SelectMultiple
from django.utils.translation import gettext_lazy as _

from shuup.utils.django_compat import NoReverseMatch, force_text


class NoModel:
    def __nonzero__(self):
        return False

    __bool__ = __nonzero__


class QuickAddRelatedObjectBaseMixin:
    model = NoModel()
    url = None

    def __init__(self, attrs=None, choices=(), editable_model=None):
        attrs = attrs or {}
        self.editable_model = editable_model
        if editable_model:
            attrs.update({"data-edit-model": editable_model})
        super().__init__(attrs, choices)


class QuickAddRelatedObjectSelectMixin(QuickAddRelatedObjectBaseMixin):
    def __init__(self, attrs=None, choices=(), editable_model=None, initial=None, model=None):
        """
        :param initial int: primary key of the object that is initially selected
        """
        if model is not None:
            self.model = model

        if self.model and initial:
            choices = [(initial.pk, force_text(initial))]

        super().__init__(attrs, choices, editable_model)


class QuickAddRelatedObjectMultipleSelectMixin(QuickAddRelatedObjectBaseMixin):
    def __init__(self, attrs=None, choices=(), editable_model=None, initial=None, model=None):
        """
        :param initial list[int]: list of primary keys of the objects that
            are initially selected
        """
        if model is not None:
            self.model = model

        if self.model and initial:
            choices = [(instance.pk, force_text(instance)) for instance in initial]

        super().__init__(attrs, choices, editable_model)


class QuickAddRelatedObjectSelect(QuickAddRelatedObjectSelectMixin, Select):
    template_name = "shuup/admin/forms/widgets/quick_add_select.jinja"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["quick_add_model"] = self.model
        try:
            context["quick_add_url"] = f"{force_text(self.url)}?mode=iframe&quick_add_target={name}"
        except NoReverseMatch:
            pass
        context["quick_add_btn_title"] = _("Create New")
        return context


class QuickAddRelatedObjectMultiSelect(QuickAddRelatedObjectMultipleSelectMixin, SelectMultiple):
    template_name = "shuup/admin/forms/widgets/quick_add_select.jinja"

    def get_context(self, name, value, attrs):
        attrs["multiple"] = True
        context = super().get_context(name, value, attrs)

        try:
            context["quick_add_url"] = f"{force_text(self.url)}?mode=iframe&quick_add_target={name}"
        except NoReverseMatch:
            pass

        context["quick_add_btn_title"] = _("Create New")
        return context
