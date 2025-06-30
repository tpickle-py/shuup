
from .delete import ProductDeleteView
from .edit import ProductEditView
from .edit_cross_sell import ProductCrossSellEditView
from .edit_media import ProductMediaBulkAdderView, ProductMediaEditView
from .edit_package import ProductPackageView
from .list import ProductListView
from .mass_edit import ProductMassEditView

__all__ = [
    "ProductCrossSellEditView",
    "ProductDeleteView",
    "ProductEditView",
    "ProductListView",
    "ProductPackageView",
    "ProductMediaEditView",
    "ProductMassEditView",
    "ProductMediaBulkAdderView",
]
