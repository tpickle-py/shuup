from shuup.utils import update_module_attributes

from ._basket import basket_partial
from ._product_preview import product_preview
from ._product_price import product_price

__all__ = ["basket_partial", "product_preview", "product_price"]

update_module_attributes(__all__, __name__)
