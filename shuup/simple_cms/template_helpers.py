from shuup.compat import contextfunction
from shuup.simple_cms.models import Page


class SimpleCMSTemplateHelpers(object):
    name = "simple_cms"

    @contextfunction
    def get_page_by_identifier(self, context, identifier):
        return (
            Page.objects.for_shop(context["request"].shop)
            .filter(identifier=identifier, deleted=False)
            .first()
        )

    @contextfunction
    def get_visible_pages(self, context):
        return Page.objects.visible(
            context["request"].shop, user=context["request"].user
        )
