from django.utils.translation import ugettext_lazy as _

from shuup.core.models import OrderLineType
from shuup.default_reports.forms import OrderReportForm
from shuup.default_reports.mixins import OrderReportMixin
from shuup.reports.report import ShuupReportBase
from shuup.utils.money import Money


class RefundedSalesReport(OrderReportMixin, ShuupReportBase):
    identifier = "refunded-sales"
    title = _("Refunded Sales")
    filename_template = "refunded-sales-%(time)s"
    form_class = OrderReportForm

    schema = [
        {"key": "refunded_orders", "title": _("Refunded Orders")},
        {"key": "total_refunded", "title": _("Total Refunded")},
    ]

    def get_data(self, **kwargs):
        orders = (
            super()
            .get_objects()
            .filter(lines__type=OrderLineType.REFUND)
            .distinct()[: self.queryset_row_limit]
        )

        total_refunded = Money(0, self.shop.currency)

        for order in orders:
            total_refunded += order.get_total_refunded_amount()

        data = [{"refunded_orders": len(orders), "total_refunded": total_refunded}]
        return self.get_return_data(data, has_totals=False)
