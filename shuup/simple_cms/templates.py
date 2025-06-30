from django.utils.translation import ugettext_lazy as _


class SimpleCMSDefaultTemplate(object):
    name = _("Default Page")
    template_path = "shuup/simple_cms/page.jinja"


class SimpleCMSTemplateSidebar(object):
    name = _("Page with sidebar")
    template_path = "shuup/simple_cms/page_sidebar.jinja"
