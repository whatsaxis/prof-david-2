import math

from src.core.base import DavidBase
from src.core.assume import NumberAssumptions
from src.core.io import OperatorIO


# TODO Negative numbers don't match -p patterns. This is because they are not represented as a Multiply[-1, ...]
# TODO Or we can just match with values? Somehow

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


class Rational(Number):
    """A rational number of the form a/b."""

    def __init__(self, a: int, b: int, **facts):
        if b == 0:
            raise ZeroDivisionError('Cannot define a rational number with b = 0')

        gcd = math.gcd(a, b)

        super().__init__(
            # (a // gcd, b // gcd),
            # TODO Oh lord
            a / b,

            rational=True,
            non_negative=a == 0 or (math.copysign(1, a) // math.copysign(1, b)) == 1,  # TODO replace with helper

            **facts
        )

    def __str__(self):
        return str(self.value) + 'Ⓠ'

    # def __hash__(self):
    #     return hash((str(self.a), str(self.b)))

    # @property
    # def a(self):
    #     return self.value[0]
    #
    # @property
    # def b(self):
    #     return self.value[1]

    # def __str__(self):
    #     return f'({ self.a }/{ self.b })'


class Integer(Number):
    """An integer."""

    def __init__(self, n: int, **facts):
        super().__init__(
            n,

            integer=True,
            rational=True,
            non_negative=n >= 0,

            **facts
        )

    def __str__(self):
        return str(self.value) + 'Ⓩ'


pi = Constant('π', math.pi)
e = Constant('𝑒', math.e)

