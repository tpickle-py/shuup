from django import forms
from django.utils.translation import gettext_lazy as _

from shuup.admin.utils.picotable import Column
from shuup.admin.utils.views import CreateOrUpdateView, PicotableListView
from shuup.default_tax.models import TaxRule
from shuup.utils.django_compat import format_lazy
from shuup.utils.patterns import PATTERN_SYNTAX_HELP_TEXT


class TaxRuleForm(forms.ModelForm):
    class Meta:
        model = TaxRule
        fields = [
            "tax_classes",
            "customer_tax_groups",
            "country_codes_pattern",
            "region_codes_pattern",
            "postal_codes_pattern",
            "priority",
            "override_group",
            "tax",
            "enabled",
        ]
        help_texts = {
            "country_codes_pattern": format_lazy(
                PATTERN_SYNTAX_HELP_TEXT,
                " ",
                _("Use ISO 3166-1 country codes (US, FI etc.)"),
            ),
            "region_codes_pattern": format_lazy(
                PATTERN_SYNTAX_HELP_TEXT,
                " ",
                _("Use two letter state codes for the US"),
            ),
            "postal_codes_pattern": PATTERN_SYNTAX_HELP_TEXT,
        }

    def clean(self):
        data = super().clean()
        data["country_codes_pattern"] = data["country_codes_pattern"].upper()
        return data


class TaxRuleEditView(CreateOrUpdateView):
    model = TaxRule
    template_name = "shuup/default_tax/admin/edit.jinja"
    form_class = TaxRuleForm
    context_object_name = "tax_rule"
    add_form_errors_as_messages = True


class TaxRuleListView(PicotableListView):
    url_identifier = "default_tax.tax_rule"
    model = TaxRule

    default_columns = [
        Column("id", _("Tax Rule")),
        Column("tax", _("Tax")),
        Column("tax_classes", _("Tax Classes")),
        Column("customer_tax_groups", _("Customer Tax Groups")),
        Column("country_codes_pattern", _("Countries")),
        Column("region_codes_pattern", _("Regions")),
        Column("postal_codes_pattern", _("Postal Codes")),
        Column("priority", _("Priority")),
        Column("override_group", _("Override Group")),
        Column("enabled", _("Enabled")),
    ]
