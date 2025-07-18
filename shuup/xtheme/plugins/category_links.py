from django import forms
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from shuup.core.models import Category
from shuup.xtheme import TemplatedPlugin
from shuup.xtheme.plugins.forms import GenericPluginForm, TranslatableField
from shuup.xtheme.plugins.widgets import XThemeSelect2ModelMultipleChoiceField


class CategoryLinksConfigForm(GenericPluginForm):
    """
    A configuration form for the CategoryLinksPlugin
    """

    def populate(self):
        """
        A custom populate method to display category choices
        """
        for field in self.plugin.fields:
            if isinstance(field, tuple):
                name, value = field
                value.initial = self.plugin.config.get(name, value.initial)
                self.fields[name] = value

        self.fields["categories"] = XThemeSelect2ModelMultipleChoiceField(
            model="shuup.category",
            required=False,
            label=_("Categories"),
            initial=self.plugin.config.get("categories"),
            extra_widget_attrs={"data-search-mode": "visible"},
        )


class CategoryLinksPlugin(TemplatedPlugin):
    """
    A plugin for displaying links to visible categories on the shop front
    """

    identifier = "category_links"
    name = _("Category Links")
    template_name = "shuup/xtheme/plugins/category_links.jinja"
    cacheable = True
    editor_form_class = CategoryLinksConfigForm
    fields = [
        ("title", TranslatableField(label=_("Title"), required=False, initial="")),
        (
            "show_all_categories",
            forms.BooleanField(
                label=_("Show all categories"),
                required=False,
                initial=True,
                help_text=_("All categories are shown, even if not selected"),
            ),
        ),
        "categories",
    ]

    def get_cache_key(self, context, **kwargs) -> str:
        selected_categories = self.config.get("categories", [])
        show_all_categories = self.config.get("show_all_categories", True)
        title = self.get_translated_value("title")
        return str((get_language(), selected_categories, show_all_categories, title))

    def get_context_data(self, context):
        """
        A custom get_context_data method to return only visible categories
        for request customer.
        """
        selected_categories = self.config.get("categories", [])
        show_all_categories = self.config.get("show_all_categories", True)
        request = context.get("request")
        categories = Category.objects.all_visible(customer=request.customer, shop=request.shop).prefetch_related(
            "translations"
        )
        if not show_all_categories:
            categories = categories.filter(id__in=selected_categories)
        return {
            "title": self.get_translated_value("title"),
            "categories": categories,
        }
