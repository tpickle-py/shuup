from django.conf import settings
from django.db import models
from django.db.transaction import atomic
from django.utils.crypto import get_random_string
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from enumfields import Enum, EnumIntegerField

from shuup.core.fields import InternalIdentifierField, MeasurementField, QuantityField
from shuup.core.models import ShuupModel
from shuup.core.signals import shipment_deleted, shipment_sent
from shuup.core.utils.units import get_shuup_volume_unit
from shuup.utils.analog import define_log_model

__all__ = ("Shipment", "ShipmentProduct")


class ShipmentStatus(Enum):
    NOT_SENT = 0
    SENT = 1
    RECEIVED = 2  # if the customer deigns to tell us
    ERROR = 10
    DELETED = 20

    class Labels:
        NOT_SENT = _("Not sent")
        SENT = _("Sent")
        RECEIVED = _("Received")
        ERROR = _("Error")
        DELETED = _("Deleted")


class ShipmentType(Enum):
    OUT = 0
    IN = 1

    class Labels:
        OUT = _("outgoing")
        IN = _("incoming")


class ShipmentQueryset(models.QuerySet):
    def all_except_deleted(self, language=None, shop=None):
        return self.exclude(status=ShipmentStatus.DELETED)

    def sent(self):
        return self.filter(status=ShipmentStatus.SENT)

    def out_only(self):
        return self.filter(type=ShipmentType.OUT)


class Shipment(ShuupModel):
    order = models.ForeignKey(
        "Order",
        blank=True,
        null=True,
        related_name="shipments",
        on_delete=models.PROTECT,
        verbose_name=_("order"),
    )
    supplier = models.ForeignKey(
        "Supplier",
        related_name="shipments",
        on_delete=models.PROTECT,
        verbose_name=_("supplier"),
    )

    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_("created on"))
    status = EnumIntegerField(ShipmentStatus, default=ShipmentStatus.NOT_SENT, verbose_name=_("status"))
    tracking_code = models.CharField(max_length=64, blank=True, verbose_name=_("tracking code"))
    tracking_url = models.URLField(blank=True, verbose_name=_("tracking url"))
    description = models.CharField(max_length=255, blank=True, verbose_name=_("description"))
    volume = MeasurementField(
        unit=get_shuup_volume_unit(),
        verbose_name=format_lazy(_("volume ({})"), get_shuup_volume_unit()),
    )
    weight = MeasurementField(
        unit=settings.SHUUP_MASS_UNIT,
        verbose_name=format_lazy(_("weight ({})"), settings.SHUUP_MASS_UNIT),
    )
    identifier = InternalIdentifierField(unique=True)
    type = EnumIntegerField(ShipmentType, default=ShipmentType.OUT, verbose_name=_("type"))

    objects = ShipmentQueryset.as_manager()

    class Meta:
        verbose_name = _("shipment")
        verbose_name_plural = _("shipments")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.identifier:
            if self.order and self.order.pk:
                prefix = f"{self.order.pk}/{self.order.shipments.count()}/"
            else:
                prefix = ""
            self.identifier = prefix + get_random_string(32)

    def __repr__(self):  # pragma: no cover
        return f"<Shipment {self.pk} (tracking {self.tracking_code!r}, created {self.created_on})>"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for product_id in self.products.values_list("product_id", flat=True):
            self.supplier.update_stock(product_id=product_id)

    def delete(self, using=None):
        raise NotImplementedError("Error! Not implemented: `Shipment` -> `delete()`. Use `soft_delete()` instead.")

    @atomic
    def soft_delete(self, user=None):
        if self.status == ShipmentStatus.DELETED:
            return
        self.status = ShipmentStatus.DELETED
        self.save(update_fields=["status"])
        for product_id in self.products.values_list("product_id", flat=True):
            self.supplier.update_stock(product_id=product_id)
        if self.order:
            self.order.update_shipping_status()
        shipment_deleted.send(sender=type(self), shipment=self)

    def is_deleted(self):
        return bool(self.status == ShipmentStatus.DELETED)

    def is_sent(self):
        return bool(self.status == ShipmentStatus.SENT)

    def cache_values(self):
        """
        (Re)cache `.volume` and `.weight` for this Shipment from within the ShipmentProducts.
        """
        total_volume = 0
        total_weight = 0
        for quantity, volume, weight in self.products.values_list("quantity", "unit_volume", "unit_weight"):
            total_volume += quantity * volume
            total_weight += quantity * weight
        self.volume = total_volume
        self.weight = total_weight

    @property
    def total_products(self):
        return self.products.aggregate(quantity=models.Sum("quantity"))["quantity"] or 0

    def set_sent(self):
        """
        Mark the shipment as sent.
        """
        if self.status == ShipmentStatus.SENT:
            return

        self.status = ShipmentStatus.SENT
        self.save()
        if self.order:
            self.order.update_shipping_status()
        shipment_sent.send(sender=type(self), order=self.order, shipment=self)

    def set_received(self, purchase_prices=None, created_by=None):
        """
        Mark the shipment as received.

        In case shipment is incoming, add stock adjustment for each
        shipment product in this shipment.

        :param purchase_prices: a dict mapping product ids to purchase prices
        :type purchase_prices: dict[shuup.shop.models.Product, decimal.Decimal]
        :param created_by: user who set this shipment received
        :type created_by: settings.AUTH_USER_MODEL
        """
        self.status = ShipmentStatus.RECEIVED
        self.save()
        if self.order:
            self.order.update_shipping_status()
        if self.type == ShipmentType.IN:
            for product_id, quantity in self.products.values_list("product_id", "quantity"):
                purchase_price = purchase_prices.get(product_id, None) if purchase_prices else None
                self.supplier.adjust_stock(
                    product_id=product_id,
                    delta=quantity,
                    purchase_price=purchase_price or 0,
                    created_by=created_by,
                )


class ShipmentProduct(ShuupModel):
    shipment = models.ForeignKey(
        Shipment,
        related_name="products",
        on_delete=models.PROTECT,
        verbose_name=_("shipment"),
    )
    product = models.ForeignKey(
        "Product",
        related_name="shipments",
        on_delete=models.CASCADE,
        verbose_name=_("product"),
    )
    quantity = QuantityField(verbose_name=_("quantity"))

    unit_volume = MeasurementField(
        unit=get_shuup_volume_unit(),
        verbose_name=format_lazy(_("unit volume ({})"), get_shuup_volume_unit()),
    )
    unit_weight = MeasurementField(
        unit=settings.SHUUP_MASS_UNIT,
        verbose_name=format_lazy(_("unit weight ({})"), settings.SHUUP_MASS_UNIT),
    )

    class Meta:
        verbose_name = _("sent product")
        verbose_name_plural = _("sent products")

    def __str__(self):  # pragma: no cover
        return f"{self.quantity} of '{self.product}' in Shipment #{self.shipment_id}"

    def cache_values(self):
        prod = self.product
        self.unit_volume = prod.width * prod.height * prod.depth
        self.unit_weight = prod.gross_weight


ShipmentLogEntry = define_log_model(Shipment)
ShipmentProductLogEntry = define_log_model(ShipmentProduct)
