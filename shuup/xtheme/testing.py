from shuup.utils import update_module_attributes

from ._theme import override_current_theme_class

__all__ = [
    "override_current_theme_class",
]

update_module_attributes(__all__, __name__)
