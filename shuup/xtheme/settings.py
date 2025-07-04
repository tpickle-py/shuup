#: Spec string for the Xtheme admin theme context.
#:
#: You can use this to determine logic around which themes
#: are visible in your project Admin Panel. This function takes shop
#: `shuup.core.models.Shop` and should return `current_theme_classes`
#: and `current_theme` for context, where `current_theme_classes`
#: is a list of `shuup.xtheme.models.ThemeSettings`.
SHUUP_XTHEME_ADMIN_THEME_CONTEXT = "shuup.xtheme.admin_module.utils.get_theme_context"

#: Spec to control Xtheme resource injections.
#:
#: Include your template names here to prevent xtheme
#: injecting resources. This does not expect the template
#: to exist.
#:
#: Can be useful in situations, where you have `html` and `body`
#: HTML tags inside the actual template structure.
SHUUP_XTHEME_EXCLUDE_TEMPLATES_FROM_RESOUCE_INJECTION = [
    "notify/admin/script_item_editor.jinja",
]
