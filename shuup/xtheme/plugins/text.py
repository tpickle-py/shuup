from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from shuup.admin.forms.widgets import TextEditorWidget
from shuup.xtheme.plugins._base import Plugin
from shuup.xtheme.plugins.forms import TranslatableField


class TextPlugin(Plugin):
    """
    Very basic Markdown rendering plugin.
    """

    identifier = "text"
    name = "Text"
    fields = [
        (
            "text",
            TranslatableField(label=_("text"), required=False, widget=TextEditorWidget),
        )
    ]

    def render(self, context):  # doccov: ignore
        text = self.get_translated_value("text", default="")
        return mark_safe(text)
