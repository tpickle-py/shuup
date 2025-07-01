from django.utils.translation import ugettext_lazy as _

from shuup.admin.base import AdminModule
from shuup.admin.utils.urls import admin_url


class PrintoutsAdminModule(AdminModule):
    name = _("Printouts")

    def get_urls(self):
        return [
            admin_url(
                r"^printouts/delivery/(?P<shipment_pk>\d+)/$",
                "shuup.order_printouts.admin_module.views.get_delivery_pdf",
                name="printouts.delivery_pdf",
            ),
            admin_url(
                r"^printouts/delivery/html/(?P<shipment_pk>\d+)/$",
                "shuup.order_printouts.admin_module.views.get_delivery_html",
                name="printouts.delivery_html",
            ),
            admin_url(
                r"^printouts/delivery/email/(?P<shipment_pk>\d+)/$",
                "shuup.order_printouts.admin_module.views.send_delivery_email",
                name="printouts.delivery_email",
            ),
            admin_url(
                r"^printouts/confirmation/(?P<order_pk>\d+)/$",
                "shuup.order_printouts.admin_module.views.get_confirmation_pdf",
                name="printouts.confirmation_pdf",
            ),
            admin_url(
                r"^printouts/confirmation/html/(?P<order_pk>\d+)/$",
                "shuup.order_printouts.admin_module.views.get_confirmation_html",
                name="printouts.confirmation_html",
            ),
            admin_url(
                r"^printouts/confirmation/email/(?P<order_pk>\d+)/$",
                "shuup.order_printouts.admin_module.views.send_confirmation_email",
                name="printouts.confirmation_email",
            ),
        ]
