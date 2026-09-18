import math

from src.core.base import DavidBase
from src.core.assume import NumberAssumptions
from src.core.error import DavidIsAngry
from src.core.io import OperatorIO


class Number(DavidBase, OperatorIO):
    """Number base class."""

    def __init__(self, value: int | float | None, **facts):
        super().__init__(NumberAssumptions.create(**facts))

        self.value = value

    def __str__(self):
        # TODO The only argument I can think of for not converting to str() is so that collecting coefficients becomes
        # TODO redundant. This (1) increases chance of collisions and (2) has the weird hash(-1) == hash(-2) in CPython.
        return str(self.value) + 'ⓝ'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        # TODO Better solution (do we need it?)
        return self.value == other

    def __hash__(self):
        return hash(str(self.value))


class Real(Number):
    """A real number."""

    def __init__(self, n: int | float, **facts):
        super().__init__(
            n,

            non_negative=n >= 0 if isinstance(n, int | float) else False,

            **facts
        )

    def __hash__(self):
        return hash(('real', self.value))

    def __str__(self):
        return str(self.value) + 'Ⓡ'


class Constant(Number):

    def __init__(self, symbol: str, approx: float):
        super().__init__(approx)

        self.symbol = symbol

    def __str__(self):
        return self.symbol


class ImaginaryUnit(Number):

    def __init__(self):
        super().__init__(None)

    def __str__(self):
        return '𝑖'


# noinspection PyPep8Naming
def Complex(re: float, im: float):
    return re + im * ImaginaryUnit()


class Natural(Number):
    """A natural number."""

    def __init__(self, n: int, **facts):
        super().__init__(
            n,

            integer=True,
            rational=True,
            non_negative=n >= 0,

            **facts
        )

        if n < 0:
            raise DavidIsAngry('Cannot instantiate a negative natural number!')

    def __str__(self):
        return str(self.value) + 'Ⓩ'


minus_one = Constant('-1', -1)

pi = Constant('π', math.pi)
e = Constant('𝑒', math.e)

