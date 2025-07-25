import six
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from shuup.admin.modules.settings.forms import ColumnSettingsForm
from shuup.admin.modules.settings.view_settings import ViewSettings
from shuup.admin.toolbar import JavaScriptActionButton, PostActionButton, Toolbar
from shuup.utils.django_compat import resolve, reverse
from shuup.utils.importing import load


class ListSettingsView(FormView):
    form_class = ColumnSettingsForm
    template_name = "shuup/admin/edit_settings.jinja"

    def dispatch(self, request, *args, **kwargs):
        module_str = "{}:{}".format(request.GET.get("module"), request.GET.get("model"))
        self.return_url = reverse("shuup_admin:{}.list".format(request.GET.get("return_url")))
        match = resolve(self.return_url)
        view_context = load(f"{match.func.__module__}:{match.func.__name__}")

        default_columns = view_context.default_columns
        self.model = load(module_str)
        self.settings = ViewSettings(self.model, default_columns, view_context)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()
        return ColumnSettingsForm(self.settings, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        for col in self.settings.columns:
            key = self.settings.get_settings_key(col.id)
            initial.update({key: self.settings.get_config(col.id)})
        return initial

    def form_valid(self, form):
        ordered_columns = self.request.POST.get("ordering", "").split("|")
        for idx, ordered_col in enumerate(ordered_columns):
            col_data = {"ordering": idx, "active": True}
            self.settings.set_config(ordered_col, col_data, use_key=True)

        for col, _val in six.iteritems(form.cleaned_data):
            if col in ordered_columns:
                continue
            col_data = {"ordering": 99999, "active": False}
            self.settings.set_config(col, col_data, use_key=True)

        messages.success(self.request, _("Settings saved."), fail_silently=True)
        return HttpResponseRedirect(self.return_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["toolbar"] = Toolbar(
            [
                PostActionButton(
                    icon="fa fa-save",
                    form_id="settings_form",
                    text=_("Save"),
                    extra_css_class="btn-success",
                ),
                JavaScriptActionButton(
                    icon="fa fa-cog",
                    text=_("Reset Defaults"),
                    onclick="resetDefaultValues()",
                ),
            ],
            view=self,
        )
        context["defaults"] = "|".join([self.settings.get_settings_key(c.id) for c in self.settings.default_columns])
        return context
