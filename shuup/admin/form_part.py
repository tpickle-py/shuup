from typing import Any, List, Optional, Tuple, Union

from django.core.exceptions import ValidationError
from django.db.transaction import atomic
from django.http import HttpResponseRedirect

from shuup.admin.signals import object_created, object_saved, view_form_valid
from shuup.admin.utils.urls import get_model_url
from shuup.admin.utils.views import add_create_or_change_message
from shuup.apps.provides import get_provide_objects
from shuup.utils.form_group import FormDef, FormGroup


class TemplatedFormDef(FormDef):
    def __init__(self, name, form_class, template_name, required=True, kwargs=None):
        self.template_name = template_name
        super().__init__(name=name, form_class=form_class, required=required, kwargs=kwargs)


class FormPart:
    priority: int = 0

    def __init__(self, request, object=None):
        self.request = request
        self.object = object

    def get_form_defs(self):
        return ()

    def form_valid(self, form):
        pass


class FormPartsViewMixin:
    fields: Union[Tuple, List] = ()  # Dealt with by the FormGroup
    request: Optional[Any] = None
    form_part_class_provide_key: Optional[str] = None
    base_form_part_classes: Union[Any, Any] = ()

    def get_form_class(self):
        return None  # Dealt with by `get_form`; this will just squelch Django warnings

    def get_form_part_classes(self):
        form_part_classes = list(self.base_form_part_classes) + list(
            get_provide_objects(self.form_part_class_provide_key)
        )
        return form_part_classes

    def get_form_parts(self, object):
        form_part_classes = self.get_form_part_classes()
        form_parts = [form_part_class(request=self.request, object=object) for form_part_class in form_part_classes]
        form_parts.sort(key=lambda form_part: getattr(form_part, "priority", 0))
        return form_parts

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        instance = kwargs.pop("instance", None)
        if not instance.pk:
            kwargs["initial"] = dict(self.request.GET.items())
        fg = FormGroup(**kwargs)
        form_parts = self.get_form_parts(instance)
        for form_part in form_parts:
            for form_def in form_part.get_form_defs():
                fg.form_defs[form_def.name] = form_def
        fg.instantiate_forms()
        return fg


class SaveFormPartsMixin:
    request: Any = None  # Placate "missing field" errors
    object: Any = None  # --"--

    @atomic()
    def save_form_parts(self, form):
        # trigger signal for extra form validations
        try:
            view_form_valid.send(sender=type(self), view=self, form=form, request=self.request)
        except ValidationError:
            return self.form_invalid(form)

        is_new = not self.object.pk
        form_parts = self.get_form_parts(self.object)
        for form_part in form_parts:
            retval = form_part.form_valid(form)

            if retval is not None:  # Allow a form part to change the identity of the object
                self.object = retval
                for form_part in form_parts:
                    form_part.object = self.object
        if is_new:
            object_created.send(sender=type(self.object), object=self.object, request=self.request)

        object_saved.send(sender=type(self.object), object=self.object, request=self.request)
        self._add_create_or_change_message(self.request, self.object, is_new)

        if self.request.GET.get("redirect") and not self.request.POST.get("__next"):
            return HttpResponseRedirect(self.request.GET.get("redirect"))

        if hasattr(self, "get_success_url"):
            return HttpResponseRedirect(self.get_success_url())

        if is_new:
            return HttpResponseRedirect(get_model_url(self.object, shop=self.request.shop))
        else:
            return HttpResponseRedirect(self.request.path)

    def _add_create_or_change_message(self, request, object, is_new):
        add_create_or_change_message(request, object, is_new)
