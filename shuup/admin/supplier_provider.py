from shuup.utils.importing import cached_load


class DefaultSupplierProvider:
    @classmethod
    def get_supplier(cls, request, **kwargs):
        return None


def get_supplier(request, **kwargs):
    return cached_load("SHUUP_ADMIN_SUPPLIER_PROVIDER_SPEC").get_supplier(
        request, **kwargs
    )
