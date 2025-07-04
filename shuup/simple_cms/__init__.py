from django.utils.translation import gettext_lazy as _

import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = __name__
    verbose_name = _("Content Pages")
    label = "shuup_simple_cms"
    default_auto_field = "django.db.models.BigAutoField"

    provides = {
        "front_urls_post": ["shuup.simple_cms.urls:urlpatterns"],
        "admin_module": ["shuup.simple_cms.admin_module:SimpleCMSAdminModule"],
        "front_template_helper_namespace": ["shuup.simple_cms.template_helpers:SimpleCMSTemplateHelpers"],
        "xtheme_layout": [
            "shuup.simple_cms.layout:PageLayout",
        ],
        "xtheme_plugin": ["shuup.simple_cms.plugins:PageLinksPlugin"],
        "simple_cms_template": [
            "shuup.simple_cms.templates:SimpleCMSDefaultTemplate",
            "shuup.simple_cms.templates:SimpleCMSTemplateSidebar",
        ],
        "admin_page_form_part": ["shuup.simple_cms.admin_module.form_parts:CMSOpenGraphFormPart"],
    }

    def ready(self):
        import reversion

        from shuup.simple_cms.models import Page

        reversion.register(Page._parler_meta.root_model)
        from shuup.utils.djangoenv import has_installed

        if has_installed("shuup.xtheme"):
            from django.db.models.signals import post_save

            from shuup.xtheme.cache import bump_xtheme_cache

            post_save.connect(bump_xtheme_cache, sender=Page)


default_app_config = __name__ + ".AppConfig"
