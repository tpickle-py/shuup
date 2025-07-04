from django.utils.translation import gettext_lazy as _

from shuup.admin.utils.picotable import ChoicesFilter, Column, TextFilter
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView
from shuup.core.models import OrderStatus, OrderStatusManager, OrderStatusRole
from shuup.utils.multilanguage_model_form import MultiLanguageModelForm


class OrderStatusForm(MultiLanguageModelForm):
    class Meta:
        model = OrderStatus
        exclude = [
            "default",
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.instance.pk and OrderStatusManager().is_default(self.instance):
            del self.fields["identifier"]
            del self.fields["role"]
            del self.fields["ordering"]
            del self.fields["is_active"]

    def clean(self):
        if self.instance.pk and OrderStatusManager().is_default(self.instance):
            data = self.cleaned_data
            data["identifier"] = self.instance.identifier
            return data

        qs = OrderStatus.objects.filter(identifier=self.cleaned_data["identifier"])
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            self.add_error("identifier", _("Identifier already exists."))

        return super().clean()

    def save(self, commit=True):
        self.instance.identifier = self.cleaned_data["identifier"]
        return super().save(commit)


class OrderStatusEditView(CreateOrUpdateView):
    model = OrderStatus
    form_class = OrderStatusForm
    template_name = "shuup/admin/orders/status.jinja"
    context_object_name = "status"


class OrderStatusListView(PicotableListView):
    model = OrderStatus
    default_columns = [
        Column(
            "identifier",
            _("Identifier"),
            linked=True,
            filter_config=TextFilter(operator="startswith"),
        ),
        Column(
            "name",
            _("Name"),
            linked=True,
            filter_config=TextFilter(operator="startswith", filter_field="translations__name"),
        ),
        Column(
            "public_name",
            _("Public Name"),
            linked=False,
            filter_config=TextFilter(operator="startswith", filter_field="translations__name"),
        ),
        Column(
            "role",
            _("Role"),
            linked=False,
            filter_config=ChoicesFilter(choices=OrderStatusRole.choices),
        ),
        Column(
            "default",
            _("Default"),
            linked=False,
            filter_config=ChoicesFilter([(False, _("yes")), (True, _("no"))]),
        ),
        Column(
            "allowed_next_statuses",
            _("Allowed Next Status"),
            linked=False,
            display="get_allowed_next_statuses_display",
        ),
        Column(
            "visible_for_customer",
            _("Visible For Customer"),
            linked=False,
            filter_config=ChoicesFilter([(False, _("yes")), (True, _("no"))]),
        ),
        Column(
            "is_active",
            _("Active"),
            linked=False,
            filter_config=ChoicesFilter([(False, _("yes")), (True, _("no"))]),
        ),
    ]

    def get_allowed_next_statuses_display(self, instance):
        order_status_names = [order_status.name for order_status in instance.allowed_next_statuses.all()]
        return ", ".join(order_status_names) if order_status_names else _("No allowed next status.")
