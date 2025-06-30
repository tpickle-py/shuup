

from django.forms import Textarea


class XthemeCodeEditorWidget(Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        attrs_for_textarea = attrs.copy()
        attrs_for_textarea["id"] += "-snippet"
        attrs_for_textarea["class"] += " xtheme-code-editor-textarea"
        return super().render(name, value, attrs_for_textarea)
