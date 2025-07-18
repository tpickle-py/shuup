from shuup.apps import AppConfig
from shuup.utils import update_module_attributes

from ._theme import (
    Theme,
    get_current_theme,
    get_middleware_current_theme,
    get_theme_by_identifier,
    get_theme_cache_key,
    set_current_theme,
    set_middleware_current_theme,
)
from .plugins._base import Plugin, TemplatedPlugin, templated_plugin_factory

__all__ = [
    "Plugin",
    "TemplatedPlugin",
    "Theme",
    "get_current_theme",
    "get_theme_by_identifier",
    "set_current_theme",
    "templated_plugin_factory",
    "get_theme_cache_key",
    "get_middleware_current_theme",
    "set_middleware_current_theme",
]

XTHEME_GLOBAL_VIEW_NAME = "_XthemeGlobalView"


class XThemeAppConfig(AppConfig):
    name = "shuup.xtheme"
    verbose_name = "Shuup Extensible Theme Engine"
    label = "shuup_xtheme"
    default_auto_field = "django.db.models.BigAutoField"

    provides = {
        "front_urls_pre": [__name__ + ".urls:urlpatterns"],
        "xtheme_plugin": [
            "shuup.xtheme.plugins.image:ImagePlugin",
            "shuup.xtheme.plugins.category_links:CategoryLinksPlugin",
            "shuup.xtheme.plugins.products:ProductsFromCategoryPlugin",
            "shuup.xtheme.plugins.products:ProductHighlightPlugin",
            "shuup.xtheme.plugins.products:ProductCrossSellsPlugin",
            "shuup.xtheme.plugins.products:ProductSelectionPlugin",
            "shuup.xtheme.plugins.products_async:ProductsFromCategoryPlugin",
            "shuup.xtheme.plugins.products_async:ProductHighlightPlugin",
            "shuup.xtheme.plugins.products_async:ProductCrossSellsPlugin",
            "shuup.xtheme.plugins.products_async:ProductSelectionPlugin",
            "shuup.xtheme.plugins.snippets:SnippetsPlugin",
            "shuup.xtheme.plugins.social_media_links:SocialMediaLinksPlugin",
            "shuup.xtheme.plugins.text:TextPlugin",
        ],
        "xtheme_layout": [
            "shuup.xtheme.layout.ProductLayout",
            "shuup.xtheme.layout.CategoryLayout",
            "shuup.xtheme.layout.AnonymousContactLayout",
            "shuup.xtheme.layout.ContactLayout",
            "shuup.xtheme.layout.PersonContactLayout",
            "shuup.xtheme.layout.CompanyContactLayout",
        ],
        "admin_module": [
            "shuup.xtheme.admin_module:XthemeAdminModule",
            "shuup.xtheme.admin_module:XthemeFontsAdminModule",
            "shuup.xtheme.admin_module:XthemeSnippetsAdminModule",
        ],
        "admin_object_selector": [
            "shuup.xtheme.object_selector:FontAdminObjectSelector",
        ],
        "xtheme_resource_injection": ["shuup.xtheme.resources:inject_global_snippet"],
        "admin_template_injector": ["shuup.xtheme.admin_injector.XthemeAdminTemplateInjector"],
    }

    def ready(self):
        import shuup.xtheme.signal_handlers  # noqa: F401


default_app_config = "shuup.xtheme.XThemeAppConfig"

update_module_attributes(__all__, __name__)
