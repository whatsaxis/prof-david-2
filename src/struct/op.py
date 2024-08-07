import math
import functools

from operator import add, mul, pow
from collections import defaultdict

from src.core.base import DavidBase
from src.core.assume import OperatorAssumptions, Commutative, Associative
from src.core.io import OperatorIO
# from src.manipulate.eq import eq_type

from src.struct.number import Constant, ImaginaryUnit, Number, Real, Integer, Rational

from typing import Optional, Callable

# TODO Find a more suitable name for this file. Damn the operator module!
# TODO [https://stackoverflow.com/questions/34330284/what-is-the-risk-of-collisions-when-relying-on-python-hash-function]


def internalize(obj, *, convert_negatives=True):
    """Function to convert primitives to internal objects."""

    # TODO library-wide preparation function

    if isinstance(obj, int):
        if convert_negatives and obj < 0 and obj != -1:
            # TODO i hate this
            return Multiply(Integer(abs(obj)), Integer(-1))

        return Integer(obj)
    if isinstance(obj, float):
        import warnings
        warnings.warn('Real instantiated!', FutureWarning)

        return Real(obj)

    return obj


class Operator(DavidBase, OperatorIO):
    """Operator base class."""

    def __init__(self, eval_fn: Optional[Callable], identity: Optional[int | float], *terms, freq=None, **facts):
        from src.manipulate.basic import absorb

        super().__init__(OperatorAssumptions.create(**facts))

        self._regenerate_caches()

        self._terms = []

        # TODO Make frequency tables ONLY for commutative
        # TODO Make frequency tables only generate when needed (maybe? defeats the point?)

        for t in terms:
            # TODO This is ugly
            if type(t) == type(self) and self.ask(Associative):
                at = absorb(t)

                if isinstance(at, Operator):
                    self.terms += at.terms
                else:
                    self.append(at)

                continue

            self.terms.append(absorb(internalize(t)))

        self._hash_cache = None
        self.is_absorbed = False
        self.freq_table = None

        if freq is None:
            self._regenerate_freq()
        else:
            self.freq_table = freq

        self.eval_fn = eval_fn
        self.identity = internalize(identity)

    """Internal"""

    def _regenerate_caches(self):
        """Regenerates the caches."""

        self._hash_cache = None
        self.is_absorbed = False

        # functools.cached_property() regenerates the cache if the property does not exist in the object's __dict__.
        # By popping the current property from the object, we regenerate these values.
        self.__dict__.pop('has_wilds', None)
        self.__dict__.pop('num_sequence', None)
        self.__dict__.pop('has_unknowns', None)

    def _regenerate_freq(self):
        """Regenerates the frequency table."""

        # TODO thank f*ck O(2n) = O(n)
        self.freq_table = defaultdict(lambda: 0)

        for t in self.terms:
            self.freq_table[t] += 1

    """Properties"""

    @functools.cached_property
    def has_wilds(self):
        # TODO Cache and change on editing terms
        from src.struct.unknown import Wild

        return any(
            t.has_wilds
            if isinstance(t, Operator)
            else isinstance(t, Wild)
            for t in self
        )

    @functools.cached_property
    def num_sequence(self):
        from src.struct.unknown import Wild

        return sum(
            t.num_sequence
            if isinstance(t, Operator)
            else (1 if isinstance(t, Wild) and t.sequence else 0)
            for t in self
        )

    @functools.cached_property
    def has_unknowns(self):
        # TODO Cache and change on editing terms
        from src.struct.unknown import Unknown

        return self.has_wilds or any(
            t.has_unknowns
            if isinstance(t, Operator)
            else isinstance(t, Unknown)
            for t in self
        )

    """Term Manipulation"""

    # Access by index

    # TODO Issue with adding items being REALLY slow as it grows. Is it due to the hash table? Probably.

    def __getitem__(self, idx: int):
        return self.terms[idx]

    def __setitem__(self, idx: int, value):
        old_value = self.terms[idx]
        self.terms[idx] = value

        # Update frequencies
        self.freq_table[old_value] -= 1
        self.freq_table[value] += 1

        self._regenerate_caches()

    """Terms"""

    @property
    def terms(self):
        return self._terms

    @terms.setter
    def terms(self, new_terms):
        self._terms = new_terms

        self._regenerate_freq()
        self._regenerate_caches()

    def append(self, term):
        self._terms.append(term)

        self.freq_table[term] += 1
        self._regenerate_caches()

    def pop(self, idx: int):
        t = self.terms.pop(idx)

        self.freq_table[t] -= 1
        self._regenerate_caches()

        return t

    def __hash__(self):
        if self._hash_cache is not None:
            return self._hash_cache

        if self.ask(Commutative):
            term_hash = sum(hash(t) for t in self.terms)
        else:
            term_hash = tuple(self.terms)

        self._hash_cache = hash((self.__class__, term_hash))

        return self._hash_cache

    """Iteration"""

    def __len__(self):
        return len(self.terms)

    def __iter__(self):
        yield from self.terms

    """Representation"""

    def __str__(self):
        return f'{ self.__class__.__name__ }[{ ", ".join(str(t) for t in self.terms) }]'

    def __repr__(self):
        return str(self)

    def copy(self):
        """Creates an identical copy of this structure."""

        c = type(self)(*self.terms, freq=self.freq_table)
        c.assumptions = self.assumptions

        return c

    def duplicate(self, *terms, empty=False, freq=None):
        """Creates an empty container identical to this structure."""

        if empty:
            return type(self)()

        c = type(self)(*terms, freq=freq)

        c.assumptions = self.assumptions

        return c

    def eval(self, force=False):
        """Evaluates constant terms for a given operator."""

        if isinstance(self, Power):
            be, pe = [t.eval(force=force) for t in self]

            if not (isinstance(be, Number) and isinstance(pe, Number) and not isinstance(be, ImaginaryUnit) and not isinstance(pe, ImaginaryUnit)):
                return self.duplicate(be, pe)

            if pe.value >= 0 or force:
                return internalize(self.eval_fn(be.value, pe.value))

            return self.duplicate(be, pe)

        if isinstance(self, Log):
            base, arg = [t.eval(force=force) for t in self]

            if not (isinstance(base, Number) and isinstance(arg, Number)):
                return self.duplicate(base, arg)

            value = internalize(self.eval_fn(base.value, arg.value))

            # TODO We need a better way to differentiate between integers, reals, etc..
            if isinstance(value.value, int) or force:
                return value

            return self.duplicate(base, arg)

        # TODO fix this dumb piece of sh*t and move it out of the operator class

        const = []
        non_const = []

        all_number = True

        for t in self:
            if isinstance(t, Operator) and not isinstance(t, Power):
                term_eval = t.eval(force=force)

                if not isinstance(term_eval, Number):
                    all_number = False

                    non_const.append(term_eval)
                else:
                    const.append(term_eval)
            elif isinstance(t, Power):
                term_eval = t.eval(force=force)

                if isinstance(term_eval, Number) and (force or isinstance(term_eval.value, int)):
                    const.append(term_eval)
                else:
                    all_number = False
                    non_const.append(term_eval)
            elif isinstance(t, Number) and not isinstance(t, ImaginaryUnit):
                if isinstance(t, Constant) and not force:
                    continue

                const.append(t)
            else:
                all_number = False

                non_const.append(t.eval(force=force))

        constant_term = internalize(self.eval_fn(*(t.value for t in const)), convert_negatives=not force)
        # print(self, constant_term, self.eval_fn(*(t.value for t in const)))

        if all_number:
            return constant_term
        else:
            if const:
                return self.duplicate(constant_term, *non_const)

            return self.duplicate(*non_const)

    def order_fast(self):
        """Generates a cheap ordered representation (hash-based)."""

        # TODO I don't know how to make this otherwise. I just need it to be CONSISTENT.
        # TODO Biggest problem with powers whose exponent is symbolic. Things like (a + b + c)^n. How do you even order that?

        return self.duplicate(
            *sorted(
                (term for term in self.terms),
                key=lambda t: hash(t)
            )
        )


class Add(Operator, OperatorIO):

    def __init__(self, *terms, freq=None):
        super().__init__(
            lambda *c: functools.reduce(add, c, 0),
            0,
            *terms,
            freq=freq,

            commutative=True,
            associative=True,
            unary=False
        )


class Multiply(Operator):

    def __init__(self, *terms, freq=None):
        super().__init__(
            lambda *c: functools.reduce(mul, c, 1),
            1,
            *terms,
            freq=freq,

            commutative=True,
            associative=True,
            unary=False
        )


class Power(Operator):

    # TODO This shouldn't even have a frequency table
    def __init__(self, base, exp, *, freq=None):
        super().__init__(
            lambda b, e: pow(b, e),
            1,
            base, exp,
            freq=freq,

            commutative=False,
            associative=False,
            unary=False
        )


# TODO Log
class Log(Operator):

    def __init__(self, base, arg, *, freq=None):
        super().__init__(
            lambda b, a: math.log(a, b),
            None,
            base, arg,
            freq=freq,

            commutative=False,
            associative=False,
            unary=False
        )

    @property
    def base(self):
        return self.terms[0]

    @property
    def arg(self):
        return self.terms[1]

    def __str__(self):
        return f'Log❲{ self.base }❳[{ self.arg }]'


class Container(Operator):
    # TODO Container

    def __init__(self, *terms, inside: Operator):
        super().__init__(
            inside.eval_fn,
            inside.identity,
            *terms,

            commutative=inside.ask(Commutative),
            associative=False,
            unary=False
        )
