from shuup.core.models import Shop
from shuup.core.utils.shops import get_shop_from_host
from shuup.utils.importing import cached_load


class DefaultShopProvider:
    @classmethod
    def get_shop(cls, request, **kwargs):
        shop = getattr(request, "_cached_default_shop_provider_shop", None)
        if shop:
            return shop

        host = request.META.get("HTTP_HOST")
        if host:
            shop = get_shop_from_host(host)

        if not shop:
            shop = Shop.objects.first()

        # cache shop as we already calculated it
        request._cached_default_shop_provider_shop = shop
        return shop


def get_shop(request, **kwargs):
    return cached_load("SHUUP_REQUEST_SHOP_PROVIDER_SPEC").get_shop(request, **kwargs)
