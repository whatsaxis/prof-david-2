import math
from fractions import Fraction

from src.core.base import DavidBase
from src.manipulate.basic import DavidObject, absorb
from src.struct.number import Constant, ImaginaryUnit, Number, e, minus_one, pi
from src.struct.op import Add, Log, Multiply, Operator, Power, Trig, internalize
from src.struct.unknown import Unknown, Wild


def is_pure_number(term) -> bool:
    """
    True if ``term`` is built entirely from Numbers exactly representable as a Fraction
    (e.g. Power[2, 1/2] is sqrt(2), NOT a rational, and must NOT be folded)
    """

    if isinstance(term, Constant) and term != minus_one:
        return False

    if term == minus_one:
        return True

    if isinstance(term, Number):
        return True

    if isinstance(term, (Unknown, Wild)):
        return False

    if isinstance(term, Add) or isinstance(term, Multiply):
        return all(is_pure_number(t) for t in term)

    if isinstance(term, Power):
        base, exp = term

        if not is_pure_number(base) or not is_pure_number(exp):
            return False

        exponent_value = to_fraction(exp)
        return exponent_value.denominator == 1

    if isinstance(term, Log):
        base, arg = term

        if not is_pure_number(base) or not is_pure_number(arg):
            return False

        if base != e:
            log = math.log(to_fraction(arg), to_fraction(base))
        else:
            log = math.log(to_fraction(arg))

        return log == int(log)

    if isinstance(term, Trig):
        # TODO This is not a good solution
        # multiples = {0, pi/2, pi, 3*pi/2, 2*pi}
        #
        # return term in multiples
        return False

    return False


def is_numeric(term) -> bool:
    """
    True if term contains only numbers.
    """

    if isinstance(term, Number):
        return True

    if isinstance(term, (Unknown, Wild)):
        return False

    if isinstance(term, Operator):
        return all(is_numeric(t) for t in term)


def to_fraction(term) -> Fraction:
    """
    Evaluate a purely numeric subtree (as verified by is_pure_number) to an exact Fraction
    """

    if not is_pure_number(term):
        return term

    if term == minus_one:
        return Fraction(-1)

    if isinstance(term, Number) and not isinstance(term, Constant):
        return Fraction(term.value)

    if isinstance(term, Add):
        total = Fraction(0)

        for t in term:
            total += to_fraction(t)

        return total

    if isinstance(term, Multiply):
        product = Fraction(1)

        for t in term:
            product *= to_fraction(t)

        return product

    if isinstance(term, Power):
        base, exp = term
        exponent_value = to_fraction(exp)

        # By the time to_fraction runs, is_pure_number should already
        # have confirmed exponent_value comes out to a whole number
        # (denominator == 1) - see is_pure_number's Power case above.
        return to_fraction(base) ** int(exponent_value)

    if isinstance(term, Log):
        base, arg = term
        return Fraction(math.log(to_fraction(arg), to_fraction(base)))

    raise TypeError(f"to_fraction called on non-pure-number term: {term!r}")


def from_fraction(frac: Fraction):
    """
    Convert a Fraction() back into David Operators
    """

    if frac.denominator == 1:
        return internalize(frac.numerator)

    if frac.numerator == 1:
        return Power(internalize(frac.denominator), internalize(-1))

    return Multiply(internalize(frac.numerator), Power(internalize(frac.denominator), internalize(-1)))


def _eval_power(term: Power, force=False):
    """Evaluates a power numerically."""

    base, exponent = [evaluate(t, force=force) for t in term]

    is_evaluable = (
        isinstance(base, Number) and isinstance(exponent, Number)
        and not isinstance(base, ImaginaryUnit) and not isinstance(exponent, ImaginaryUnit)
        and not isinstance(base, Constant) and not isinstance(exponent, Constant)
    )

    if not is_evaluable:
        return term.duplicate(base, exponent)

    exponent_is_integer = exponent.value == int(exponent.value)

    if exponent_is_integer:
        # Always exact regardless of `force`, and safe regardless
        # of the exponent's sign, since Fraction handles negative
        # integer powers exactly (no floats involved anywhere).
        result = to_fraction(base) ** int(exponent.value)
        return from_fraction(result)

    if force:
        # Explicitly opted into a (likely lossy) numeric approximation
        return internalize(base.value**exponent.value)

    return term.duplicate(base, exponent)


def _eval_log(term: Log, force=False):
    """
    Evaluates a log numerically.
    """

    base, arg = [evaluate(t, force=force) for t in term]

    is_evaluable = (
        isinstance(base, Number) and isinstance(arg, Number)
        and not isinstance(base, ImaginaryUnit) and not isinstance(arg, ImaginaryUnit)
        and not isinstance(base, Constant) and not isinstance(arg, Constant)
    )

    if not is_evaluable:
        return term.duplicate(base, arg)

    value = internalize(term.eval_fn(base.value, arg.value))

    # Technically misses exact non-integer rational results. I really don't care
    if isinstance(value.value, int) or force:
        return internalize(value)

    return term.duplicate(base, arg)


def _eval_generic(term, force=False):
    """Evaluation for other operators"""

    foldable = []
    rest = []

    for t in term:
        evaluated = evaluate(t, force=force)

        if isinstance(evaluated, ImaginaryUnit):
            rest.append(evaluated)
            continue

        # Preserve constants unevaluated (apart from the special -1)
        if isinstance(evaluated, Constant) and evaluated != minus_one and not force:
            rest.append(evaluated)
            continue

        if is_pure_number(evaluated):
            foldable.append(
                to_fraction(evaluated)
            )
        else:
            rest.append(evaluated)

    if not foldable:
        return term.duplicate(*rest)

    total = term.eval_fn(*foldable)

    # Return a plain numerical value if force=True
    if force:
        return absorb(term.duplicate(internalize(float(total)), *rest))

    if not rest:
        return from_fraction(total)

    if total == term.identity:
        # Don't reinsert 0 into a sum or 1 into a product when there
        # are other terms - matches what p+0->p / 1*p->p would do
        # anyway, just resolved earlier.
        return term.duplicate(*rest)

    return term.duplicate(from_fraction(total), *rest)


def evaluate(term: DavidObject, force=False):
    """Evaluates constant terms for a given operator."""

    if isinstance(term, Number | Unknown):
        return term

    if isinstance(term, Power):
        return internalize(_eval_power(term, force=force))

    if isinstance(term, Log):
        return internalize(_eval_log(term, force=force))

    return internalize(_eval_generic(term, force=force))
