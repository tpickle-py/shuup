from shuup.utils import update_module_attributes

from ._context import TaxingContext
from ._line_tax import LineTax, SourceLineTax
from ._module import TaxModule, get_tax_module, should_calculate_taxes_automatically
from ._price import TaxedPrice
from ._tax_summary import TaxSummary
from ._taxable import TaxableItem

__all__ = [
    "LineTax",
    "SourceLineTax",
    "TaxModule",
    "TaxSummary",
    "TaxableItem",
    "TaxedPrice",
    "TaxingContext",
    "get_tax_module",
    "should_calculate_taxes_automatically",
]

update_module_attributes(__all__, __name__)
