from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class OrderReferenceNumberMethod(Enum):
    UNIQUE = "unique"
    RUNNING = "running"
    SHOP_RUNNING = "shop_running"

    class Labels:
        UNIQUE = _("unique")
        RUNNING = _("running")
        SHOP_RUNNING = _("shop running")
