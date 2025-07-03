from django.utils.translation import gettext_lazy as _


class SimpleCMSDefaultTemplate:
    name = _("Default Page")
    template_path = "shuup/simple_cms/page.jinja"


class SimpleCMSTemplateSidebar:
    name = _("Page with sidebar")
    template_path = "shuup/simple_cms/page_sidebar.jinja"
