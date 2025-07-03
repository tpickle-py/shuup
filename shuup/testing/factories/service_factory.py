# Service-related factory functions (Payment and Shipping)
from shuup.core.models import (
    CustomCarrier,
    CustomPaymentProcessor,
    FixedCostBehaviorComponent,
    PaymentMethod,
    ShippingMethod,
    WaivingCostBehaviorComponent,
)

from .shared import DEFAULT_IDENTIFIER, get_default_shop
from .tax_factory import get_default_tax_class


def get_custom_payment_processor():
    return _get_service_provider(CustomPaymentProcessor)


def get_payment_processor_with_checkout_phase():
    raise NotImplementedError("get_payment_processor_with_checkout_phase requires PaymentWithCheckoutPhase model.")


def get_custom_carrier():
    return _get_service_provider(CustomCarrier)


def _get_service_provider(model):
    identifier = model.__name__
    service_provider = model.objects.filter(identifier=identifier).first()
    if not service_provider:
        service_provider = model.objects.create(
            identifier=identifier,
            name=model.__name__,
        )
        assert service_provider.pk and service_provider.identifier == identifier
    return service_provider


def get_default_payment_method():
    return get_payment_method()


def get_payment_method(shop=None, price=None, waive_at=None, name=None):
    return _get_service(
        PaymentMethod,
        CustomPaymentProcessor,
        name=name,
        shop=shop,
        price=price,
        waive_at=waive_at,
    )


def get_default_shipping_method():
    return get_shipping_method()


def get_shipping_method(shop=None, price=None, waive_at=None, name=None):
    return _get_service(
        ShippingMethod,
        CustomCarrier,
        name=name,
        shop=shop,
        price=price,
        waive_at=waive_at,
    )


def _get_service(service_model, provider_model, name, shop=None, price=None, waive_at=None):
    default_shop = get_default_shop()
    if shop is None:
        shop = default_shop
    if shop == default_shop and not price and not waive_at and not name:
        identifier = DEFAULT_IDENTIFIER
    else:
        identifier = f"{name}-{shop.pk}-{repr(price)}-{repr(waive_at)}"
    service = service_model.objects.filter(identifier=identifier).first()
    if not service:
        provider = _get_service_provider(provider_model)
        service = provider.create_service(
            None,
            identifier=identifier,
            shop=shop,
            enabled=True,
            name=(name or service_model.__name__),
            tax_class=get_default_tax_class(),
        )
        if price and waive_at is None:
            service.behavior_components.add(FixedCostBehaviorComponent.objects.create(price_value=price))
        elif price:
            service.behavior_components.add(
                WaivingCostBehaviorComponent.objects.create(price_value=price, waive_limit_value=waive_at)
            )
    assert service.pk and service.identifier == identifier
    assert service.shop == shop
    return service
