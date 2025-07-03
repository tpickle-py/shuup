from typing import Any, List, Optional

from django import forms


class ColumnSettingsForm(forms.Form):
    settings: Optional[Any] = None
    non_selected: List[str] = []
    selected: List[str] = []

    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        self.selected = [settings.get_settings_key(c.id) for c in settings.active_columns]
        self.non_selected = [settings.get_settings_key(c.id) for c in settings.inactive_columns]

        for column in settings.column_spec:
            settings_key = settings.get_settings_key(column.id)
            self.fields[settings_key] = forms.BooleanField(label=column.title, required=False)
