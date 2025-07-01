from django.utils.translation import ugettext_lazy as _

from shuup.xtheme.layout import Layout


class CategoryLayout(Layout):
    identifier = "xtheme-category-layout"

    def get_help_text(self, context):
        category = context.get("category")
        if not category:
            return ""
        return _(f"Content in this placeholder is shown for {category.name} category only.")

    def is_valid_context(self, context):
        return bool(context.get("category"))

    def get_layout_data_suffix(self, context):
        return "{}-{}".format(self.identifier, context["category"].pk)
