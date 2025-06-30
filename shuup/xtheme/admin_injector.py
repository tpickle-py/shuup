import logging
from typing import TYPE_CHECKING, Optional

from django.template import loader

from shuup.admin.base import AdminTemplateInjector
from shuup.core.models import Shop, Supplier
from shuup.xtheme.models import AdminThemeSettings

LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.auth import get_user_model

    User = get_user_model()


class XthemeAdminTemplateInjector(AdminTemplateInjector):
    @classmethod
    def get_admin_template_snippet(
        cls, place: str, shop: "Shop", user: "User", supplier: "Optional[Supplier]"
    ):
        if place == "head_end":
            admin_theme = AdminThemeSettings.objects.filter(shop=shop).first()
            if admin_theme and admin_theme.active:
                try:
                    return loader.render_to_string(
                        "shuup/xtheme/admin/admin_theme_injection.jinja",
                        context={
                            "admin_theme": admin_theme,
                        },
                    )
                except Exception:
                    LOGGER.exception("Failed to render snippet.")
