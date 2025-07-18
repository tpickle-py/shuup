from django import forms
from django.conf import settings
from django.contrib import messages
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from shuup.admin.supplier_provider import get_supplier
from shuup.admin.toolbar import PostActionButton, Toolbar, URLActionButton
from shuup.admin.utils.urls import get_model_url
from shuup.core.excs import InvalidRefundAmountException, NoRefundToCreateException, RefundExceedsAmountException
from shuup.core.models import Order, OrderLineType, Shop
from shuup.utils.django_compat import reverse
from shuup.utils.money import Money


class RefundForm(forms.Form):
    line_number = forms.ChoiceField(
        label=_("Line"),
        required=False,
        help_text=_(
            "The line to refund. To refund an amount not associated with any line, select 'Refund arbitrary amount'."
        ),
    )
    quantity = forms.DecimalField(
        required=False,
        min_value=0,
        initial=0,
        label=_("Quantity"),
        help_text=_("The number of units to refund."),
    )
    text = forms.CharField(
        max_length=255,
        label=_("Line Text/Comment"),
        required=False,
        help_text=_("The text describing the nature of the refund and/or the reason for the refund."),
    )
    amount = forms.DecimalField(
        required=False,
        initial=0,
        label=_("Amount"),
        help_text=_("The amount including tax to refund."),
    )
    restock_products = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Restock products"),
        help_text=_("If checked, the quantity is adding back into the sellable product inventory."),
    )

    def clean_line_number(self):
        # TODO Test clean functions or use a custom validator
        line_number = self.cleaned_data["line_number"]
        return line_number if line_number != "" else None

    def clean_quantity(self):
        # TODO Test clean functions or use a custom validator
        quantity = self.cleaned_data["quantity"]
        return quantity if quantity != 0 else None

    def clean_amount(self):
        # TODO Test clean functions or use a custom validator
        amount = self.cleaned_data["amount"]
        return amount if amount != 0 else None


class OrderCreateRefundView(UpdateView):
    model = Order
    template_name = "shuup/admin/orders/create_refund.jinja"
    context_object_name = "order"
    form_class = forms.formset_factory(RefundForm, extra=1)

    def get_queryset(self):
        shop_ids = Shop.objects.get_for_user(self.request.user).values_list("id", flat=True)
        return Order.objects.exclude(deleted=True).filter(shop_id__in=shop_ids)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Create Refund -- %s") % context["order"]
        context["toolbar"] = Toolbar(
            [
                PostActionButton(
                    icon="fa fa-check-circle",
                    form_id="create_refund",
                    text=_("Create Refund"),
                    extra_css_class="btn-success",
                )
            ],
            view=self,
        )

        # Allowing full refunds for suppliers would block the refunds for
        # rest of the suppliers since full refund can only be created once
        supplier = context["supplier"] = get_supplier(self.request)
        if not supplier:
            context["toolbar"].append(
                URLActionButton(
                    url=reverse(
                        "shuup_admin:order.create-full-refund",
                        kwargs={"pk": self.object.pk},
                    ),
                    icon="fa fa-dollar",
                    text=_("Refund Entire Order"),
                    extra_css_class="btn-info",
                    disable_reason=_("This order already has existing refunds") if self.object.has_refunds() else None,
                )
            )

        # Setting the line_numbers choices dynamically creates issues with the blank formset,
        # So adding that to the context to be rendered manually
        context["line_number_choices"] = self._get_line_number_choices(supplier)

        lines = lines = self.object.lines.all()
        if supplier:
            lines = lines.filter(supplier=supplier)
        context["json_line_data"] = {line.ordering: self._get_line_data(self.object, line) for line in lines}
        return context

    def _get_line_data(self, order, line):
        shop = order.shop
        total_price = line.taxful_price.value if shop.prices_include_tax else line.taxless_price.value
        base_data = {
            "id": line.id,
            "type": "other" if line.quantity else "text",
            "text": line.text,
            "quantity": line.quantity - line.refunded_quantity,
            "sku": line.sku,
            "baseUnitPrice": line.base_unit_price.value,
            "unitPrice": total_price / line.quantity if line.quantity else 0,
            "unitPriceIncludesTax": shop.prices_include_tax,
            "amount": line.max_refundable_amount.value,
            "errors": "",
            "step": "",
        }
        if line.product:
            shop_product = line.product.get_shop_instance(shop)
            supplier = line.supplier
            stock_status = supplier.get_stock_status(line.product.pk) if supplier else None
            base_data.update(
                {
                    "type": "product",
                    "product": {"id": line.product.pk, "text": line.product.name},
                    "step": shop_product.purchase_multiple,
                    "logicalCount": stock_status.logical_count if stock_status else 0,
                    "physicalCount": stock_status.physical_count if stock_status else 0,
                    "salesDecimals": line.product.sales_unit.decimals if line.product.sales_unit else 0,
                    "salesUnit": line.product.sales_unit.symbol if line.product.sales_unit else "",
                }
            )
        return base_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("instance")
        return kwargs

    def _get_line_text(self, line):
        text = f"line {line.ordering + 1}: {line.text}"
        if line.sku:
            text += f" (SKU {line.sku})"
        return text

    def _get_line_number_choices(self, supplier):
        lines = self.object.lines.all()
        if supplier:
            lines = lines.filter(supplier=supplier)

        line_number_choices = [("", "---")]
        if settings.SHUUP_ALLOW_ARBITRARY_REFUNDS and self.object.get_total_unrefunded_amount(supplier).value > 0:
            line_number_choices += [("amount", _("Refund arbitrary amount"))]
        return line_number_choices + [
            (line.ordering, self._get_line_text(line))
            for line in lines
            if (
                (
                    (line.type == OrderLineType.PRODUCT and line.max_refundable_quantity > 0)
                    or (
                        line.type != OrderLineType.PRODUCT
                        and line.max_refundable_amount.value > 0
                        and line.max_refundable_quantity > 0
                    )
                )
                and line.type != OrderLineType.REFUND
            )
        ]

    def get_form(self, form_class=None):
        formset = super().get_form(form_class)

        # Line orderings are zero-indexed, but shouldn't display that way
        choices = self._get_line_number_choices(get_supplier(self.request))
        for form in formset.forms:
            form.fields["line_number"].choices = choices
        formset.empty_form.fields["line_number"].choices = choices

        return formset

    def _get_refund_line_info(self, order, data, supplier):
        refund_line_info = {}
        amount_value = data.get("amount", 0) or 0
        line_number = data.get("line_number")
        quantity = data.get("quantity", 0) or 1
        restock_products = data.get("restock_products")

        if line_number != "amount":
            lines = order.lines.filter(ordering=line_number)
            if supplier:
                lines = lines.filter(supplier=supplier)

            line = lines.first()

            if not line:
                return None
            refund_line_info["line"] = line
            refund_line_info["quantity"] = quantity
            refund_line_info["restock_products"] = bool(restock_products)
        else:
            refund_line_info["line"] = "amount"
            refund_line_info["text"] = data.get("text")
            refund_line_info["quantity"] = 1
        refund_line_info["amount"] = Money(amount_value, order.currency)
        return refund_line_info

    def form_valid(self, form):
        order = self.object
        supplier = get_supplier(self.request)
        refund_lines = []

        for refund in form.cleaned_data:
            line = self._get_refund_line_info(order, refund, supplier)
            if line:
                refund_lines.append(line)

        try:
            order.create_refund(refund_lines, created_by=self.request.user, supplier=supplier)
        except RefundExceedsAmountException:
            messages.error(self.request, _("Refund amount exceeds order amount."))
            return self.form_invalid(form)
        except InvalidRefundAmountException:
            messages.error(self.request, _("Refund amounts should match sign on parent line."))
            return self.form_invalid(form)
        messages.success(self.request, _("Refund created."))
        return HttpResponseRedirect(get_model_url(order))


class FullRefundConfirmationForm(forms.Form):
    restock_products = forms.BooleanField(required=False, initial=True, label=_("Restock products"))


class OrderCreateFullRefundView(UpdateView):
    model = Order
    template_name = "shuup/admin/orders/create_full_refund.jinja"
    context_object_name = "order"
    form_class = FullRefundConfirmationForm

    def get_queryset(self):
        shop_ids = Shop.objects.get_for_user(self.request.user).values_list("id", flat=True)
        return Order.objects.exclude(deleted=True).filter(shop_id__in=shop_ids)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Create Full Refund -- %s") % context["order"]
        context["toolbar"] = Toolbar(
            [
                URLActionButton(
                    url=reverse("shuup_admin:order.create-refund", kwargs={"pk": self.object.pk}),
                    icon="fa fa-check-circle",
                    text=_("Cancel"),
                    extra_css_class="btn-danger",
                ),
            ],
            view=self,
        )
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("instance")
        return kwargs

    def form_valid(self, form):
        order = self.object
        restock_products = bool(form.cleaned_data.get("restock_products"))

        try:
            order.create_full_refund(restock_products)
        except NoRefundToCreateException:
            messages.error(self.request, _("Could not create a full refund."))
            return self.form_invalid(form)

        messages.success(self.request, _("Full refund created."))
        return HttpResponseRedirect(get_model_url(order))
