import math
import itertools
import collections

from src.core.base import DavidBase
from src.manipulate.basic import absorb
from src.manipulate.helpers import contains_var, descend_struct
from src.manipulate.simplify import ExpandIdentities, simplify
from src.ntheory.factor import factors
from src.struct.number import Natural, Number, e, pi, ImaginaryUnit

from src.struct.op import Cos, Log, Operator, Sin, Trig, internalize
from src.struct.unknown import Unknown
from src.struct.relation import Equals, Relation

from src.struct.op import Add, Multiply, Power
from src.struct.unknown import Wild

from src.manipulate.pattern import Pattern
from src.manipulate.substitute import Identity, IdentitySet, apply_greedily, apply_until_constant

from src.manipulate.eq import eq_struct


def differentiate(expr: DavidBase, var: Unknown):
    """Automatic differentiation of an expression with respect to variable ``var``."""

    if isinstance(expr, Number):
        return internalize(0)
    elif isinstance(expr, Unknown):
        if expr == var:
            return internalize(1)
        else:
            return internalize(0)
    elif isinstance(expr, Add):
        add_term = Add()

        for term in expr:
            add_term.append(differentiate(term, var))

        # print('diff', expr, ' ---> ', absorb(add_term))
        return simplify(absorb(add_term))
    elif isinstance(expr, Multiply):
        # Product rule
        #
        # For many functions:
        # (fgh)' = f'gh + fg'h + fgh'

        add_term = Add()

        for i, diff_term in enumerate(expr):
            mult_term = Multiply()

            for j, non_diff_term in enumerate(expr):
                if i == j:
                    mult_term.append(differentiate(diff_term, var))
                else:
                    mult_term.append(non_diff_term)

            """
            TODO Potentially more efficient:
            
            y' = y[f'/f + g'/g + h'/h + ...]
            
            From logarithmic differentiation
            To be fair, it would have to be multiplied out anyway. The current way is more human.
            """

            add_term.append(mult_term)

        # print('diff', expr, ' ---> ', simplify(absorb(add_term)))
        return simplify(absorb(add_term))
    elif isinstance(expr, Power):
        # Use of logarithmic differentiation
        # d/dx f(x)^g(x) = f(x)^g(x) * [g'(x) ln f(x) + g(x) f'(x) / f(x)]

        f, g = expr.base, expr.exp

        diff = f**g * (
            differentiate(g, var) * Log(e, f) +
            (g/f) * differentiate(f, var)
        )
        # print('diff', expr, ' ---> ', simplify(absorb(diff)))
        return simplify(absorb(diff))
    elif isinstance(expr, Log):
        # d/dx log_a f(x) = f'(x) / [f(x) ln(a)]

        base, f = expr.base, expr.arg

        diff = differentiate(f, var) / (
            f * Log(e, base)
        )
        # print('diff', expr, ' ---> ', absorb(diff))
        return simplify(absorb(diff))
    elif isinstance(expr, Trig):
        # Chain rule first

        if isinstance(expr, Sin):
            diff = differentiate(expr.inside, var) * Cos(expr.inside)
        if isinstance(expr, Cos):
            diff = - differentiate(expr.inside, var) * Sin(expr.inside)

        return simplify(absorb(diff))
