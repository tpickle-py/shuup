from django.utils.translation import gettext_lazy as _

from shuup.notify.base import Event, Variable
from shuup.notify.typology import Email, Model


class CompanyAccountCreated(Event):
    identifier = "company_account_created"

    contact = Variable("CompanyContact", type=Model("shuup.CompanyContact"))
    customer_email = Variable(_("Customer Email"), type=Email)
