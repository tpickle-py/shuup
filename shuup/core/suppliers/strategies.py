

class FirstSupplierStrategy(object):
    def get_supplier(self, **kwargs):
        shop_product = kwargs["shop_product"]
        return shop_product.suppliers.enabled(shop=shop_product.shop).first()
