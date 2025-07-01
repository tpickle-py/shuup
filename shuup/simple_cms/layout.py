from django.utils.translation import ugettext_lazy as _

from shuup.xtheme.layout import Layout


class PageLayout(Layout):
    identifier = "simple-cms-page-layout"
    help_text = _("Content in this placeholder is shown for this page only.")

    def get_help_text(self, context):
        page = context.get("page")
        if not page:
            return ""
        return _(f"Content in this placeholder is shown for {page.title} only.")

    def is_valid_context(self, context):
        return bool(context.get("page"))

    def get_layout_data_suffix(self, context):
        return "{}-{}".format(self.identifier, context["page"].pk)
