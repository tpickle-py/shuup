from shuup.core.models import Supplier


class UsernameSupplierProvider:
    @classmethod
    def get_supplier(cls, request, **kwargs):
        return Supplier.objects.filter(identifier=request.user.username).first()


class RequestSupplierProvider:
    @classmethod
    def get_supplier(cls, request, **kwargs):
        return getattr(request, "supplier", None)


class FirstSupplierProvider:
    @classmethod
    def get_supplier(cls, request, **kwargs):
        return Supplier.objects.first()
