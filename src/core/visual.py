from src.core.base import DavidBase

from src.manipulate.basic import absorb
from src.manipulate.eq import eq_struct
from src.manipulate.helpers import is_negative_coefficient
from src.manipulate.pattern import Pattern
from src.manipulate.simplify import simplify

from src.struct.op import Log, Operator, Add, Multiply, Power
from src.struct.relation import Relation
from src.struct.unknown import Unknown, Wild
from src.struct.number import Constant, ImaginaryUnit, Number, Real, Rational, Integer, e, pi


def tex(obj: DavidBase, *, frac=True):
    """Converts an expression to a LaTeX string."""

    # → Numbers
    if isinstance(obj, Number):
        if obj == pi:
            return r'\pi'
        if obj == e:
            return r'e'
        if isinstance(obj, ImaginaryUnit):
            return r'i'

        return str(obj.value)

    # → Unknowns
    if isinstance(obj, Unknown):
        # TODO Support for subscripts.

        return str(obj.symbol)

    # → Relations
    if isinstance(obj, Relation):
        return f'{ tex(obj.left, frac=frac) } { obj.symbol } { tex(obj.right, frac=frac) }'

    # → Operators
    if isinstance(obj, Operator):

        obj = absorb(obj)

        # → Addition
        if isinstance(obj, Add):
            s = ''

            for i, term in enumerate(obj):
                if i == 0:
                    s += tex(term, frac=frac)
                    continue

                if is_negative_coefficient(term):
                    s += ' - ' + tex(simplify(-term))
                else:
                    s += ' + ' + tex(term)

                # s += ' + ' + tex(term, frac=frac)

            return s

        # → Multiplication
        if isinstance(obj, Multiply):

            if frac:
                numerator = ''
                denominator = ''

                for i, term in enumerate(obj):
                    # Addition must be surrounded by brackets in multiplication [e.g. ab(c + d)]
                    # TODO When there are multiple numbers, how is this handled? Or a minus sign? Automatically collect? But that's not very nice.
                    if isinstance(term, Add):
                        numerator += '(' + tex(term) + ')'

                    # TODO Add a non-fraction mode too!
                    # Negative exponents are flipped and placed on the denominator
                    elif isinstance(term, Power):
                        base, exp = term

                        if is_negative_coefficient(exp):
                            denominator += tex(simplify(term.duplicate(base, -exp)))
                        else:
                            numerator += tex(term)

                    else:
                        if i != 0:
                            numerator += r' \cdot ' + tex(term)
                        else:
                            numerator += tex(term)

                numerator = '1' if not numerator else numerator

                if denominator:
                    return fr'\frac{{{ numerator }}}{{{ denominator }}}'

                return numerator

            else:
                o = []

                for term in obj:
                    t = tex(term, frac=frac)

                    if isinstance(term, Add):
                        t = '(' + t + ')'

                    o.append(t)
                return r' \cdot '.join(o)

        # → Exponentiation
        if isinstance(obj, Power):
            base, exp = obj

            p, q, r = Wild('p'), Wild('q'), Wild('r')

            root_test = [m for m in Pattern(p**(q/r)).match(obj)] + [m for m in Pattern(p**(Power(r, -1))).match(obj)]

            print(obj, root_test)

            if root_test:
                match = root_test[0]

                if len(match[1]) == 0:
                    subs = match[0]
                    p, q, r = subs['p'], subs.get('q', None), subs['r']

                    if q:
                        return fr'{ tex(p) }^{{\frac{{{ tex(q) }}}{{{ tex(r) }}}}}'

                    return fr'\sqrt[{ tex(r) }]{{{ tex(p) }}}'

            if isinstance(base, Add | Power):
                return fr'\left({ tex(base, frac=frac) }\right)^{{{ tex(exp, frac=frac) }}}'

            return fr'{ tex(base, frac=frac) }^{{{ tex(exp, frac=frac) }}}'

        # → Logarithms
        if isinstance(obj, Log):
            base, arg = obj.base, obj.arg

            return fr'\log_{{{ tex(base, frac=frac) }}}({ tex(arg, frac=frac) })'

        return tex(obj)
