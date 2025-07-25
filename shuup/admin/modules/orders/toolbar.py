import warnings

from django.utils.translation import gettext_lazy as _

from shuup.admin.toolbar import (
    DropdownActionButton,
    DropdownItem,
    PostActionButton,
    PostActionDropdownItem,
    Toolbar,
    URLActionButton,
)
from shuup.apps.provides import get_provide_objects
from shuup.core.models import OrderStatus
from shuup.utils.deprecation import RemovedFromShuupWarning
from shuup.utils.django_compat import reverse


class OrderDetailToolbar(Toolbar):
    def __init__(self, order):
        self.order = order
        super().__init__()
        self.build()

    def build(self):
        self._build_action_button()
        self._build_order_set_state_button()
        self._build_edit_button()
        self._build_provided_toolbar_buttons()

    def _build_action_button(self):
        action_menu_items = []

        for button in get_provide_objects("admin_order_toolbar_action_item"):
            if button.visible_for_object(self.order):
                action_menu_items.append(button(object=self.order))

        if action_menu_items:
            self.append(
                DropdownActionButton(
                    action_menu_items,
                    icon="fa fa-star",
                    text=_("Actions"),
                    extra_css_class="btn-inverse",
                )
            )

    def _build_order_set_state_button(self):
        set_status_menu_items = []
        for status in self.order.status.allowed_next_statuses.all().order_by("ordering"):
            btn = PostActionDropdownItem(
                post_url=reverse("shuup_admin:order.set-status", kwargs={"pk": self.order.pk}),
                name="status",
                value=status.pk,
                text=status.name,
            )
            set_status_menu_items.append(btn)

        if set_status_menu_items:
            self.append(
                DropdownActionButton(
                    set_status_menu_items,
                    icon="fa fa-refresh",
                    text=_("Set Status"),
                    extra_css_class="btn-primary set-status-button",
                )
            )

    # TODO TEST or REMOVE
    def _build_set_complete_button(self):
        self.append(
            PostActionButton(
                post_url=reverse("shuup_admin:order.set-status", kwargs={"pk": self.order.pk}),
                name="status",
                value=OrderStatus.objects.get_default_complete().pk,
                text=_("Set Complete"),
                icon="fa fa-check-circle",
                disable_reason=(
                    _("This order can not be set as complete at this point")
                    if not self.order.can_set_complete()
                    else None
                ),
                extra_css_class="btn-success",
            )
        )

    def _build_cancel_button(self):
        self.append(
            PostActionButton(
                post_url=reverse("shuup_admin:order.set-status", kwargs={"pk": self.order.pk}),
                name="status",
                value=OrderStatus.objects.get_default_canceled().pk,
                text=_("Cancel Order"),
                icon="fa fa-trash",
                disable_reason=(
                    _("Paid, shipped, or canceled orders cannot be canceled")
                    if not self.order.can_set_canceled()
                    else None
                ),
                extra_css_class="btn-danger btn-inverse",
            )
        )

    def _build_edit_button(self):
        self.append(
            URLActionButton(
                text=_("Edit order"),
                icon="fa fa-money",
                disable_reason=_("This order cannot modified at this point") if not self.order.can_edit() else None,
                url=reverse("shuup_admin:order.edit", kwargs={"pk": self.order.pk}),
                extra_css_class="btn-info",
            )
        )

    def _build_provided_toolbar_buttons(self):
        for button in get_provide_objects("admin_order_toolbar_button"):
            warnings.warn(
                "Warning! `admin_order_toolbar_button` provider is deprecated, "
                "use `admin_order_toolbar_action_item` instead.",
                RemovedFromShuupWarning,
                stacklevel=2,
            )
            self.append(button(self.order))


class CreatePaymentAction(DropdownItem):
    def __init__(self, object, **kwargs):
        kwargs["url"] = reverse("shuup_admin:order.create-payment", kwargs={"pk": object.pk})
        kwargs["icon"] = "fa fa-money"
        kwargs["text"] = _("Create Payment")
        super().__init__(**kwargs)

    @staticmethod
    def visible_for_object(object):
        return object.can_create_payment() and not (
            (object.is_not_paid() or object.is_deferred()) and not object.taxful_total_price
        )


class SetPaidAction(PostActionDropdownItem):
    def __init__(self, object, **kwargs):
        kwargs["post_url"] = reverse("shuup_admin:order.set-paid", kwargs={"pk": object.pk})
        kwargs["icon"] = "fa fa-exclamation-circle"
        kwargs["text"] = _("Set Paid")
        super().__init__(**kwargs)

    @staticmethod
    def visible_for_object(object):
        return (object.is_not_paid() or object.is_deferred()) and not object.taxful_total_price


class CreateRefundAction(DropdownItem):
    def __init__(self, object, **kwargs):
        kwargs["url"] = reverse("shuup_admin:order.create-refund", kwargs={"pk": object.pk})
        kwargs["icon"] = "fa fa-dollar"
        kwargs["text"] = _("Create Refund")
        super().__init__(**kwargs)

    @staticmethod
    def visible_for_object(object):
        return object.can_create_refund()


class EditAddresses(DropdownItem):
    def __init__(self, object, **kwargs):
        kwargs["url"] = reverse("shuup_admin:order.edit-addresses", kwargs={"pk": object.pk})
        kwargs["icon"] = "fa fa-address-card"
        kwargs["text"] = _("Edit Addresses")
        super().__init__(**kwargs)

    @staticmethod
    def visible_for_object(object):
        return not object.is_complete()
