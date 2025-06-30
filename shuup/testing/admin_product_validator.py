from typing import Iterable

from shuup.admin.modules.products.issues import ProductValidationIssue
from shuup.admin.modules.products.validators import AdminProductValidator
from shuup.core.models import Shop, ShopProduct, Supplier


class TestAdminProductValidator(AdminProductValidator):
    """
    Test class for validating products.
    """

    ordering = 1

    def get_validation_issues(
        shop_product: ShopProduct, shop: Shop, user, supplier: Supplier = None
    ) -> Iterable[ProductValidationIssue]:
        """
        Returns an instance of ProductValidationIssue in case a field is not valid.
        """

        yield ProductValidationIssue("This is an error", "error", code="1200")
        yield ProductValidationIssue(
            'This is a HTML <strong>warning</strong><script src="http://shuup.com/xss.js"></script>',
            "warning",
            code="warn",
            is_html=True,
        )
        yield ProductValidationIssue("This is an info", "info")
