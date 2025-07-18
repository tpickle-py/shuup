from django.template import loader
from django.utils.safestring import mark_safe

from shuup.compat import contextfunction


class TemplateHelpers:
    name = "simple_search"

    @contextfunction
    def get_search_form(self, context, template_name="shuup/simple_search/search_form.jinja"):
        """
        Get a product search form, usable e.g. for navigation bars.
        The `q` request parameter is used by default to pre-fill the search query field.
        The name of the template rendered can be overridden with the `template_name` parameter.

        :param context: Template context
        :type context: jinja2.runtime.Context
        :param template_name: Template file name
        :type template_name: str
        """
        request = context["request"]
        env = dict(context.items(), q=request.GET.get("q"))
        return mark_safe(loader.render_to_string(template_name, context=env, request=request))
