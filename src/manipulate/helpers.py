import collections

from src.core.base import DavidBase

from src.manipulate.eq import eq_struct

from src.struct.op import Multiply, Operator
from src.struct.number import Constant, ImaginaryUnit, Number, Real, Rational
from src.struct.unknown import Unknown


def is_negative_coefficient(obj: DavidBase):
    """Checks whether an object has negative coefficients."""

    # → Reals
    if isinstance(obj, Number) and not isinstance(obj, ImaginaryUnit):
        if obj.value is not None:
            return obj.value < 0

    # → Rationals
    # if isinstance(obj, Rational):
    #     return obj.a / obj.b < 0

    # → Numbers
    # if isinstance(obj, Number):
    #     return obj.value < 0

    # → Multiplication
    if isinstance(obj, Multiply):
        # obj = collect(absorb(obj))

        sign = 1

        for t in obj:
            if isinstance(t, Number) and not isinstance(t, ImaginaryUnit):
                if t.value < 0:
                    sign *= -1

        return sign == -1

    return False


def descend_struct(s: Operator, loc: list | tuple):
    """Function to descend a structure from a location tuple."""

    for p in loc:
        s = s[p]

    return s


def from_freq(freq: dict | collections.Counter):
    o = []

    for t in freq:
        o += [t.copy() for i in range(freq[t])]

    return o


def contains_var(s: Operator, var: Unknown):
    if isinstance(s, Unknown):
        return eq_struct(s, var)

    if isinstance(s, Operator):
        for t in s:
            if contains_var(t, var):
                return True

        return False
