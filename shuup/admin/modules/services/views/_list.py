from django.utils.translation import gettext_lazy as _

from shuup.admin.utils.picotable import Column, TextFilter, true_or_false_filter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import PaymentMethod, ShippingMethod
from shuup.utils.django_compat import force_text


class ServiceListView(PicotableListView):
    model = None  # Override in subclass
    columns = []
    base_columns = [
        Column(
            "name",
            _("Name"),
            sort_field="translations__name",
            filter_config=TextFilter(filter_field="translations__name", placeholder=_("Filter by name...")),
        ),
        Column(
            "choice_identifier",
            _("Service choice"),
            display="format_service_choice",
            sortable=False,
        ),
        Column("enabled", _("Enabled"), filter_config=true_or_false_filter),
        Column("shop", _("Shop")),
    ]
    toolbar_buttons_provider_key = "service_list_toolbar_provider"
    mass_actions_provider_key = "service_list_mass_actions_provider"

    def get_object_abstract(self, instance, item):
        return [
            {"text": f"{instance}", "class": "header"},
        ]

    def format_service_choice(self, instance, *args, **kwargs):
        if instance.provider:
            for choice in instance.provider.get_service_choices():
                if choice.identifier == instance.choice_identifier:
                    return force_text(choice.name)

    def get_queryset(self):
        return super().get_queryset().filter(shop=self.request.shop)


class ShippingMethodListView(ServiceListView):
    model = ShippingMethod

    def __init__(self, **kwargs):
        self.default_columns = self.base_columns + [Column("carrier", _("Carrier"))]
        super().__init__(**kwargs)


class PaymentMethodListView(ServiceListView):
    model = PaymentMethod

    def __init__(self, **kwargs):
        self.default_columns = self.base_columns + [Column("payment_processor", _("Payment Processor"))]
        super().__init__(**kwargs)
