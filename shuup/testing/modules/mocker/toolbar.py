from django.utils.translation import ugettext_lazy as _

from shuup.admin.toolbar import BaseToolbarButtonProvider, DropdownItem, URLActionButton


class MockContactToolbarButton(URLActionButton):
    def __init__(self, contact, **kwargs):
        kwargs["icon"] = "fa fa-user"
        kwargs["text"] = _("Hello") + contact.full_name
        kwargs["extra_css_class"] = "btn-info"
        kwargs["url"] = "/#mocktoolbarbutton"

        self.contact = contact

        super().__init__(**kwargs)


class MockShopToolbarButton(URLActionButton):
    def __init__(self, shop, **kwargs):
        kwargs["icon"] = "fa fa-user"
        kwargs["text"] = _("Hello") + shop.name
        kwargs["extra_css_class"] = "btn-info"
        kwargs["url"] = "/#mocktoolbarbuttonforshop"

        self.shop = shop

        super().__init__(**kwargs)

    @staticmethod
    def visible_for_object(shop):
        return shop.pk


class MockContactToolbarActionItem(DropdownItem):
    def __init__(self, object, **kwargs):
        kwargs["icon"] = "fa fa-hand-peace-o"
        kwargs["text"] = _("Hello %(name)s") % {"name": object.full_name}
        kwargs["url"] = "/#mocktoolbaractionitem"
        super().__init__(**kwargs)

    @staticmethod
    def visible_for_object(object):
        return True


class MockProductToolbarActionItem(DropdownItem):
    def __init__(self, object, **kwargs):
        kwargs["icon"] = "fa fa-female"
        kwargs["text"] = _("This is %(sku)s") % {"sku": object.sku}
        kwargs["url"] = f"#{object.sku}"
        super().__init__(**kwargs)


class MockContactGroupToolbarButton(URLActionButton):
    def __init__(self, **kwargs):
        kwargs["icon"] = "fa fa-user"
        kwargs["text"] = _("Hello")
        kwargs["extra_css_class"] = "btn-info btn-contact-group-hello"
        kwargs["url"] = "/#mocktoolbarbutton"
        super().__init__(**kwargs)


class ContactGroupPriceDisplayButtonProvider(BaseToolbarButtonProvider):
    @classmethod
    def get_buttons_for_view(cls, view):
        return [MockContactGroupToolbarButton()]
