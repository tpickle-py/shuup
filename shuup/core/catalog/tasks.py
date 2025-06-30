from shuup.core.catalog import ProductCatalog


def index_shop_product(shop_product_id: int):
    """
    Task to call the ProductCatalog to index the shop product.
    This util function can be used by a task runner to index this asynchronously.
    """
    ProductCatalog.index_shop_product(shop_product_id)


def index_product(product_id: int):
    """
    Task to call the ProductCatalog to index the product.
    This util function can be used by a task runner to index this asynchronously.
    """
    ProductCatalog.index_product(product_id)
