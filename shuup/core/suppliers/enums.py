from django.utils.translation import gettext_lazy as _
from enumfields import Enum


class StockAdjustmentType(Enum):
    INVENTORY = 1
    RESTOCK = 2
    RESTOCK_LOGICAL = 3

    class Labels:
        INVENTORY = _("inventory")
        RESTOCK = _("restock")
        RESTOCK_LOGICAL = _("restock logical")
