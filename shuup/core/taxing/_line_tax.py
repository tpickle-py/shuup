import six

import shuup.core.models
import shuup.utils.money


class LineTax:
    """
    Tax of some line.

    This is an interface for specifying taxes of an `OrderLine` or
    `SourceLine`.

    .. attribute:: tax

       (`~shuup.core.models.Tax`)
       The tax that this line is about.

    .. attribute:: name

       (`str`)
       Name of the tax.

    .. attribute:: amount

       (`~shuup.utils.money.Money`)
       Tax amount.

    .. attribute:: base_amount

       (`~shuup.utils.money.Money`)
       Amount that this tax is calculated from.
    """

    @property
    def rate(self):
        if not self.base_amount:
            return self.tax.rate
        return self.amount / self.base_amount

    @classmethod
    def from_tax(cls, tax, base_amount, **kwargs):
        """
        Create tax line for given tax and base amount.

        :type cls: type
        :type tax: shuup.core.models.Tax
        :type base_amount: shuup.utils.money.Money
        """
        return cls(
            tax=tax,
            name=tax.name,
            base_amount=base_amount,
            amount=tax.calculate_amount(base_amount),
            **kwargs,
        )


class SourceLineTax(LineTax):
    def __init__(self, tax, name, amount, base_amount):
        """
        Initialize line tax from given values.

        :type tax: shuup.core.models.Tax
        :type name: six.text_type
        :type amount: shuup.utils.money.Money
        :type base_amount: shuup.utils.money.Money
        """
        assert isinstance(tax, shuup.core.models.Tax)
        assert isinstance(name, six.text_type)
        assert isinstance(amount, shuup.utils.money.Money)
        assert isinstance(base_amount, shuup.utils.money.Money)
        self.tax = tax
        self.name = name
        self.amount = amount
        self.base_amount = base_amount

    def __repr__(self):
        return f"{type(self).__name__}({self.tax!r}, {self.name!r}, {self.amount!r}, {self.base_amount!r})"
