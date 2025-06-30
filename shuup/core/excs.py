from shuup.utils.excs import Problem


class ImmutabilityError(ValueError):
    pass


class NoShippingAddressException(Exception):
    pass


class NoProductsToShipException(Exception):
    pass


class NoPaymentToCreateException(Exception):
    pass


class NoRefundToCreateException(Exception):
    pass


class RefundArbitraryRefundsNotAllowedException(Exception):
    pass


class RefundExceedsAmountException(Exception):
    pass


class RefundExceedsQuantityException(Exception):
    pass


class InvalidRefundAmountException(Exception):
    pass


class MissingSettingException(Exception):
    pass


class ProductNotOrderableProblem(Problem):
    pass


class ProductNotVisibleProblem(Problem):
    pass


class InvalidOrderStatusError(Problem):
    pass


class ImpossibleProductModeException(ValueError):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class SupplierHasNoSupplierModules(Exception):
    pass
