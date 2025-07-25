from django.utils.translation import gettext_lazy as _

from shuup.admin.utils.picotable import Column, TextFilter
from shuup.admin.utils.views import PicotableListView
from shuup.core.models import Currency
from shuup.utils.i18n import get_current_babel_locale


class CurrencyListView(PicotableListView):
    model = Currency

    default_columns = [
        Column("name", _("Name"), display="get_currency_display", sortable=False),
        Column(
            "code",
            _("Code"),
            sort_field="code",
            filter_config=TextFilter(
                filter_field="code",
                placeholder=_("Filter by code"),
            ),
        ),
        Column(
            "decimal_places",
            _("Decimal places"),
            display="format_decimal_places",
        ),
    ]
    toolbar_buttons_provider_key = "currency_list_toolbar_provider"
    mass_actions_provider_key = "currency_list_mass_actions_provider"

    def format_decimal_places(self, instance):
        return f"{instance.decimal_places}"

    def get_currency_display(self, instance):
        locale = get_current_babel_locale()
        return locale.currencies.get(instance.code, instance.code)
