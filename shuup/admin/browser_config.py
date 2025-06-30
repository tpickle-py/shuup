from django.conf import settings
from django.templatetags.static import static

from shuup.admin.utils.permissions import has_permission
from shuup.utils.i18n import get_current_babel_locale


class BaseBrowserConfigProvider(object):
    @classmethod
    def get_browser_urls(cls, request, **kwargs):
        return {}

    @classmethod
    def get_gettings(cls, request, **kwargs):
        return {}


class DefaultBrowserConfigProvider(BaseBrowserConfigProvider):
    @classmethod
    def get_browser_urls(cls, request, **kwargs):
        return {
            "edit": "shuup_admin:edit",
            "select": "shuup_admin:select",
            "object_selector": "shuup_admin:object_selector",
            "media": (
                "shuup_admin:media.browse"
                if has_permission(request.user, "media.browse")
                else None
            ),
            "upload": (
                "shuup_admin:media.upload"
                if has_permission(request.user, "media.upload")
                else None
            ),
            "product": "shuup_admin:shop_product.list",
            "contact": "shuup_admin:contact.list",
            "setLanguage": "shuup_admin:set-language",
            "tour": "shuup_admin:tour",
            "menu_toggle": "shuup_admin:menu_toggle",
            "add_media": (
                ("shuup_admin:shop_product.add_media", (), {"pk": 99999})
                if has_permission(request.user, "shop_product.add_media")
                else None
            ),
        }

    @classmethod
    def get_gettings(cls, request, **kwargs):
        return {
            "minSearchInputLength": settings.SHUUP_ADMIN_MINIMUM_INPUT_LENGTH_SEARCH
            or 1,
            "dateInputFormat": settings.SHUUP_ADMIN_DATE_INPUT_FORMAT,
            "datetimeInputFormat": settings.SHUUP_ADMIN_DATETIME_INPUT_FORMAT,
            "timeInputFormat": settings.SHUUP_ADMIN_TIME_INPUT_FORMAT,
            "datetimeInputStep": settings.SHUUP_ADMIN_DATETIME_INPUT_STEP,
            "dateInputLocale": get_current_babel_locale().language,
            "staticPrefix": static(""),
        }
