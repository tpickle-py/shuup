# Tax-related factory functions
from decimal import Decimal

from shuup.core.models import Tax, TaxClass
from shuup.default_tax.models import TaxRule
from shuup.utils.money import Money

from .shared import DEFAULT_IDENTIFIER, DEFAULT_NAME, default_by_identifier


def get_tax(code, name, rate=None, amount=None):
    assert amount is None or isinstance(amount, Money)
    tax = Tax.objects.filter(code=code).first()
    if not tax:
        tax = Tax.objects.create(
            code=code,
            name=name,
            rate=Decimal(rate) if rate is not None else None,
            amount_value=getattr(amount, "value", None),
            currency=getattr(amount, "currency", None),
        )
        assert tax.pk
        assert name in str(tax)
    return tax


def create_default_tax_rule(tax):
    tr = TaxRule.objects.filter(tax=tax).first()
    if not tr:
        tr = TaxRule.objects.create(tax=tax)
        tr.tax_classes.add(get_default_tax_class())
    return tr


def get_default_tax():
    tax = get_tax(DEFAULT_IDENTIFIER, DEFAULT_NAME, Decimal("0.5"))
    create_default_tax_rule(tax)  # Side-effect, but useful
    return tax


def get_test_tax(rate):
    name = f"TEST_{rate}"
    return get_tax(name, name, rate)


def get_default_tax_class():
    tax_class = default_by_identifier(TaxClass)
    if not tax_class:
        tax_class = TaxClass.objects.create(
            identifier=DEFAULT_IDENTIFIER,
            name=DEFAULT_NAME,
            # tax_rate=Decimal("0.5"),
        )
        assert tax_class.pk
        assert str(tax_class) == DEFAULT_NAME
    return tax_class
