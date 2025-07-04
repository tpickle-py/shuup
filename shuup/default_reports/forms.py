from django import forms
from django.utils.translation import gettext_lazy as _

from shuup.admin.forms.fields import ObjectSelect2MultipleField
from shuup.core.models import Carrier, Contact, OrderLineType, OrderStatus, ShippingMethod, Supplier, Tax, TaxClass
from shuup.reports.forms import BaseReportForm


class OrderReportForm(BaseReportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        customer_field = ObjectSelect2MultipleField(
            label=_("Customer"),
            model=Contact,
            required=False,
            help_text=_("Filter report results by customer."),
        )
        customers = self.initial_contacts("customer")
        if customers:
            customer_field.initial = customers
            customer_field.widget.choices = [(obj.pk, obj.name) for obj in customers]
        orderer_field = ObjectSelect2MultipleField(
            label=_("Orderer"),
            model=Contact,
            required=False,
            help_text=_("Filter report results by the person that made the order."),
        )
        orderers = self.initial_contacts("orderer")
        if orderers:
            orderer_field.initial = orderers
            orderer_field.widget.choices = [(obj.pk, obj.name) for obj in orderers]
        self.fields["customer"] = customer_field
        self.fields["orderer"] = orderer_field

    def initial_contacts(self, key):
        if self.data and key in self.data:
            return Contact.objects.filter(pk__in=self.data.getlist(key))
        return []


class OrderLineReportForm(BaseReportForm):
    order_line_type = forms.MultipleChoiceField(
        label=_("Order Line Type"),
        required=False,
        initial=[OrderLineType.PRODUCT.value],
        choices=[(line_type.value, line_type.name.capitalize()) for line_type in OrderLineType],
    )  # Because value of OrderLineType.PRODUCT is 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        supplier = ObjectSelect2MultipleField(
            label=_("Suppliers"),
            model=Supplier,
            required=False,
            help_text=_("Filter order lines by suppliers."),
        )
        order_status = forms.ModelMultipleChoiceField(
            label=_("Order status"),
            required=False,
            queryset=OrderStatus.objects.all(),
            help_text=_("Filter order lines by status of their order."),
        )

        suppliers = self.get_initial_suppliers("supplier")

        if suppliers:
            supplier.initial = suppliers
            supplier.widget.choices = [(obj.pk, obj.name) for obj in suppliers]

        self.fields["supplier"] = supplier
        self.fields["order_status"] = order_status

    def get_initial_suppliers(self, key):
        if self.data and key in self.data:
            return Supplier.objects.filter(pk__in=self.data.getlist(key))
        return []


class ProductTotalSalesReportForm(OrderReportForm):
    SORT_ORDER_CHOICES = (
        ("quantity", _("Quantity")),
        ("taxless_total", _("Taxless Total")),
        ("taxful_total", _("Taxful Total")),
    )

    order_by = forms.ChoiceField(
        label=_("Sort order"),
        initial="quantity",
        required=True,
        choices=SORT_ORDER_CHOICES,
    )


class NewCustomersReportForm(BaseReportForm):
    GROUP_BY_CHOICES = (
        ("%Y", _("Year")),
        ("%Y-%m", _("Year/Month")),
        ("%Y-%m-%d", _("Year/Month/Day")),
    )

    group_by = forms.ChoiceField(
        label=_("Group by"),
        initial=GROUP_BY_CHOICES[1],
        required=True,
        choices=GROUP_BY_CHOICES,
    )


class CustomerSalesReportForm(OrderReportForm):
    SORT_ORDER_CHOICES = (
        ("order_count", _("Order Count")),
        ("average_sales", _("Average Sales")),
        ("taxless_total", _("Taxless Total")),
        ("taxful_total", _("Taxful Total")),
    )
    order_by = forms.ChoiceField(
        label=_("Sort order"),
        initial="order_count",
        required=True,
        choices=SORT_ORDER_CHOICES,
    )


class TaxesReportForm(OrderReportForm):
    tax = ObjectSelect2MultipleField(
        label=_("Tax"),
        model=Tax,
        required=False,
        help_text=_("Filter report results by tax."),
    )

    tax_class = ObjectSelect2MultipleField(
        label=_("Tax Class"),
        model=TaxClass,
        required=False,
        help_text=_("Filter report results by tax class."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data and "tax" in self.data:
            taxes = Tax.objects.filter(pk__in=self.data.getlist("tax"))
            self.fields["tax"].initial = taxes.first()
            self.fields["tax"].widget.choices = [(obj.pk, obj.name) for obj in taxes]

        if self.data and "tax_class" in self.data:
            tax_classes = TaxClass.objects.filter(pk__in=self.data.getlist("tax_class"))
            self.fields["tax_class"].initial = tax_classes
            self.fields["tax_class"].widget.choices = [(obj.pk, obj.name) for obj in tax_classes]


class ShippingReportForm(OrderReportForm):
    shipping_method = ObjectSelect2MultipleField(
        label=_("Shipping Method"),
        model=ShippingMethod,
        required=False,
        help_text=_("Filter report results by shipping method."),
    )

    carrier = ObjectSelect2MultipleField(
        label=_("Carrier"),
        model=Carrier,
        required=False,
        help_text=_("Filter report results by carrier."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.data and "shipping_method" in self.data:
            shipping_method = ShippingMethod.objects.filter(pk__in=self.data.getlist("shipping_method"))
            self.fields["shipping_method"].initial = shipping_method.first()
            self.fields["shipping_method"].widget.choices = [(obj.pk, obj.name) for obj in shipping_method]

        if self.data and "carrier" in self.data:
            carrier = Carrier.objects.filter(pk__in=self.data.getlist("carrier"))
            self.fields["carrier"].initial = carrier
            self.fields["carrier"].widget.choices = [(obj.pk, obj.name) for obj in carrier]
