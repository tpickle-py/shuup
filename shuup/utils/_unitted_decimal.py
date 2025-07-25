import decimal


class UnittedDecimal(decimal.Decimal):
    """
    Decimal with unit.

    Allows creating decimal classes that cannot be mixed, e.g. to
    prevent operations like::

        TaxfulPrice(1) + TaxlessPrice(2)

    where `TaxfulPrice` and `TaxlessPrice` are subclasses of
    `UnittedDecimal`.
    """

    @property
    def value(self):
        """
        Value of this decimal without the unit.

        :rtype: decimal.Decimal
        """
        return decimal.Decimal(self)

    def __repr__(self):
        decimal_repr = super().__repr__()
        return decimal_repr.replace("Decimal", type(self).__name__)

    def unit_matches_with(self, other):
        """
        Test if self and other have matching units.

        :rtype: bool
        """
        raise NotImplementedError("Error! Not implemented: `UnittedDecimal` -> `unit_matches_with()`.")

    def new(self, value):
        """
        Create new instance with given value using same unit as self.

        Post-condition: If ``x = y.new(v)``, then
        ``x.unit_matches_with(y) and x.value == v``.

        :type value:
        :return: Object with same type as self and matching unit, but with given decimal value.
        :rtype: UnittedDecimal
        """
        return type(self)(value)

    def _check_units_match(self, other):
        if not self.unit_matches_with(other):
            raise UnitMixupError(self, other)

    def __lt__(self, other, **kwargs):
        self._check_units_match(other)
        return super().__lt__(other, **kwargs)

    def __le__(self, other, **kwargs):
        self._check_units_match(other)
        return super().__le__(other, **kwargs)

    def __gt__(self, other, **kwargs):
        self._check_units_match(other)
        return super().__gt__(other, **kwargs)

    def __ge__(self, other, **kwargs):
        self._check_units_match(other)
        return super().__ge__(other, **kwargs)

    def __eq__(self, other, *args, **kwargs):
        if not self.unit_matches_with(other):
            return False
        return super().__eq__(other, **kwargs)

    def __ne__(self, other, *args, **kwargs):
        if not self.unit_matches_with(other):
            return True
        return super().__ne__(other, **kwargs)

    def __add__(self, other, **kwargs):
        self._check_units_match(other)
        return self.new(super().__add__(other, **kwargs))

    def __sub__(self, other, **kwargs):
        self._check_units_match(other)
        return self.new(super().__sub__(other, **kwargs))

    def __mul__(self, other, **kwargs):
        if isinstance(other, UnittedDecimal):
            raise TypeError(f"Error! Cannot multiply {self!r} with {other!r}.")
        return self.new(super().__mul__(other, **kwargs))

    def __radd__(self, other, **kwargs):
        return self.__add__(other, **kwargs)

    def __rsub__(self, other, **kwargs):
        return (-self).__add__(other, **kwargs)

    def __rmul__(self, other, **kwargs):
        return self.__mul__(other, **kwargs)

    def __truediv__(self, other, **kwargs):
        if isinstance(other, UnittedDecimal):
            self._check_units_match(other)
            return super().__truediv__(other, **kwargs)
        else:
            value = super().__truediv__(other, **kwargs)
            return self.new(value)

    def __rtruediv__(self, other, **kwargs):
        if not isinstance(other, UnittedDecimal):
            type_name = type(self).__name__
            raise TypeError(f"Error! Cannot divide non-{type_name} with {type_name}.")
        self._check_units_match(other)
        return super().__rtruediv__(other, **kwargs)

    __div__ = __truediv__
    __rdiv__ = __rtruediv__

    def __floordiv__(self, other, **kwargs):
        if not isinstance(other, UnittedDecimal):
            type_name = type(self).__name__
            msg = f"Error! Cannot floor-div {type_name} with non-{type_name}."
            raise TypeError(msg)
        self._check_units_match(other)
        return super().__floordiv__(other, **kwargs)

    def __rfloordiv__(self, other, **kwargs):
        if not isinstance(other, UnittedDecimal):
            type_name = type(self).__name__
            msg = f"Error! Cannot floor-div non-{type_name} with {type_name}."
            raise TypeError(msg)
        self._check_units_match(other)
        return super().__rfloordiv__(other, **kwargs)

    def __mod__(self, other, **kwargs):
        if not isinstance(other, UnittedDecimal):
            type_name = type(self).__name__
            raise TypeError(f"Error! Cannot modulo {type_name} with non-{type_name}.")
        self._check_units_match(other)
        return self.new(super().__mod__(other, **kwargs))

    def __divmod__(self, other, **kwargs):
        if not isinstance(other, UnittedDecimal):
            type_name = type(self).__name__
            raise TypeError(f"Error! Cannot divmod {type_name} with non-{type_name}.")
        self._check_units_match(other)
        (div, mod) = super().__divmod__(other, **kwargs)
        return (div, self.new(mod))

    def __pow__(self, other, **kwargs):
        type_name = type(self).__name__
        raise TypeError(f"Error! {type_name} cannot be powered.")

    def __neg__(self, **kwargs):
        return self.new(super().__neg__(**kwargs))

    def __pos__(self, **kwargs):
        return self.new(super().__pos__(**kwargs))

    def __abs__(self, **kwargs):
        return self.new(super().__abs__(**kwargs))

    def __int__(self, **kwargs):
        return super().__int__(**kwargs)

    def __float__(self, **kwargs):
        return super().__float__(**kwargs)

    def __round__(self, ndigits=0, **kwargs):
        value = super().__round__(ndigits, **kwargs)
        return self.new(value)

    def quantize(self, exp, *args, **kwargs):
        value = super().quantize(exp, *args, **kwargs)
        return self.new(value)

    def copy_negate(self, *args, **kwargs):
        value = super().copy_negate(*args, **kwargs)
        return self.new(value)


class UnitMixupError(TypeError):
    """
    Invoked operation for UnittedDecimal and object with non-matching unit.

    The objects involved are stored in instance variables `obj1` and
    `obj2`.  Former is instance of :class:`UnittedDecimal` or its
    subclass and the other could be any object.

    :ivar UnittedDecimal obj1: Involved object 1.
    :ivar Any obj2: Involved object 2.
    """

    def __init__(self, obj1, obj2, msg="Unit mixup"):
        self.obj1 = obj1
        self.obj2 = obj2
        super().__init__(msg)

    def __str__(self):
        super_str = super().__str__()
        return f"{super_str}: {self.obj1!r} vs {self.obj2!r}"
