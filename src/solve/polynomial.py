import math

from src.core.base import DavidBase
from src.manipulate.basic import DavidObject, absorb
from src.manipulate.eq import eq_struct
from src.manipulate.evaluate import evaluate, is_numeric
from src.manipulate.pattern import Pattern
from src.manipulate.simplify import simplify
from src.manipulate.substitute import Identity, IdentitySet, apply_until_constant
from src.struct.op import Add, Operator, Power, internalize
from src.struct.relation import Equals
from src.struct.unknown import Unknown, Wild


p, q, r, s = Wild('p'), Wild('q'), Wild('r'), Wild('s')
u, v = Wild('u', sequence=True), Wild('v', sequence=True)


def find_struct(op: DavidObject, struct: DavidObject, posn_offset=None):
    """Returns the positions of a structure within a structure."""

    if not posn_offset:
        posn_offset = tuple()

    matches = []

    if eq_struct(op, struct):
        matches.append(posn_offset)

    if isinstance(op, Operator):
        for i, t in enumerate(op):
            fs = find_struct(t, struct, posn_offset + (i,))

            if fs:
                matches.extend(fs)

    return matches


def find_var(op: DavidObject, var: Unknown, posn_offset=None):
    """Returns the positions of a variable in a structure."""

    return find_struct(op, var, posn_offset=posn_offset)

    # if not posn_offset:
    #     posn_offset = []
    #
    # if not isinstance(op, Operator):
    #     if eq_struct(op, var):
    #         return [posn_offset]
    #     return []
    #
    # positions = []
    # for i, t in enumerate(op):
    #     fv = find_var(t, var, posn_offset + [i])
    #
    #     if fv:
    #         positions.extend(fv)
    #
    # return positions




def poly_collect(poly: Add, var: Unknown):
    """
    Collects the coefficients of terms of the variable and transforms all terms into powers of the variable.
    """

    collect_powers = IdentitySet(
        Identity(var * var, var**2),
        Identity(var ** p * var, var ** (p + 1)),
        Identity(var ** p * var ** q, var ** (p + q))
    )

    i_set = IdentitySet(
        Identity(
            p * u + p * v, p * (u + v),

            # Of the form ax or ax**n
            {p: lambda m: eq_struct(m, var) or eq_struct(m, var**s)}
        )
    )

    return apply_until_constant(apply_until_constant(poly, collect_powers), i_set)


def get_poly_patterns(var: Unknown):
    def doesnt_contain_var(xp):
        return find_var(xp, var) == []

    return [
        Pattern(p, {p: doesnt_contain_var}),  # Constant terms
        Pattern(q, {q: lambda _: eq_struct(_, var)}),  # x terms TODO this is weird
        Pattern(u * var, {u: doesnt_contain_var}),  # kx terms
        Pattern(var**p, {p: is_numeric}),  # x^n terms
        Pattern(u * var**p, {u: doesnt_contain_var, p: is_numeric})  # kx^n terms
    ]


def get_poly_coefficients(expr: Add, var: Unknown):
    poly = poly_collect(expr, var)

    poly_patterns = get_poly_patterns(var)[1:]  # Exclude the constant terms

    coeffs = {}
    non_var = []

    degree = 0

    for term in poly:
        matched = False

        # print('TERM', term)
        # TODO Match top level function
        for pattern in poly_patterns:
            # print('   PATTERM', pattern.pattern)
            for match in pattern.match(term):
                # print(match)
                # Not top level match
                if len(match[1]) != 0:
                    # print('invalid')
                    continue

                # Extract coefficient and exponent from matches
                coeff = match[0].get('u', internalize(1))
                exp = match[0].get('p', internalize(1)).value

                coeffs[exp] = coeff

                if exp > degree:
                    degree = exp

                # print('valid match')
                matched = True
                break

            if matched:
                break

        if not matched:
            non_var.append(term)

    coeffs[0] = absorb(Add(*non_var))

    return degree, coeffs


def poly_solve_coeffs(degree: int, coeffs: dict):
    """Solves a polynomial given coefficients."""

    # print(degree, coeffs)

    if degree == 1:
        a, b = coeffs.get(1), coeffs.get(0, internalize(0))

        return simplify(-b / a),

    if degree == 2:

        a, b, c = coeffs.get(2), coeffs.get(1, internalize(0)), coeffs.get(0, internalize(0))


        delta = simplify(b**2 - 4*a*c)
        # print('abc ', a, b, c, 'delta', delta)

        if eq_struct(delta, internalize(0)):
            return simplify(
                -b/(2*a)
            ),
        else:
            return simplify((-b + delta**Power(2, -1)) / (2*a)), simplify((-b - delta**Power(2, -1)) / (2*a))

    # if degree == 3:
    #     a, b, c, d = coeffs.get(3), coeffs.get(2, internalize(0)), coeffs.get(1, internalize(0)), coeffs.get(0, internalize(0))
    #
    #     delta_0 = b**2 - 3*a*c
    #     delta_1 = 2*b**3 - 9*a*b*c + 27*a**2*d
    #
    #     C1 = delta_1 +


def poly_eliminate_negative_powers(poly: Add, var: Unknown):
    """Multiplies out negative powers, increasing the degree of the polynomial by the smallest negative degree."""

    degree, coeffs = get_poly_coefficients(poly, var)

    # Deal with negative powers
    # TODO Non-numeric powers?
    if any(p < 0 for p in coeffs.keys()):
        min_neg_pow = min(coeffs.keys())

        poly_2 = []
        for pt in poly:
            poly_2.append(pt * var**abs(min_neg_pow))

        return simplify(poly.duplicate(*poly_2))

    return poly


def poly_solve(degree, coeffs, var: Unknown, verbose=False):
    """
    | Solves a polynomial equation of the form a_1 x^b_1 + a_2 x^b_2 + ... + a_n = 0.
    | Note that the polynomial is assumed to be on the left.
    | Also assumed that poly_eliminate_negative_powers() has been called on the polynomial already.
    """

    from src.solve.solve import solve

    # print(coeffs)

    # Eliminate negative powers
    # x + 1 + 1/x --> x^2 + x + 1
    min_power = min(coeffs.keys())

    # TODO This shouldn't introduce extraneous solutions.

    if min_power < 0:
        coeffs = {
            exp + abs(min_power): coeff
            for exp, coeff in coeffs.items()
        }

    if verbose: print(f'        → Eliminating negative powers')

    # Check for multiples in the coefficients

    # TODO Non-numeric coefficients and powers

    zero_root_flag = False
    # TODO zero root flag

    # Factor out the maximum variable power
    # x^5 + x^3 + x^2 --> x^2(x^3 + x + 1)
    # This adds a root x=0 when we cancel these shared x^m terms out

    if eq_struct(coeffs.get(0, internalize(0)), internalize(0)):
        p_min = min([k for k in coeffs.keys() if not eq_struct(coeffs[k], internalize(0))])

        coeffs = {
            pwr - p_min: coef
            for pwr, coef in coeffs.items()
        }

        zero_root_flag = True
        degree -= p_min

    sols = []

    if zero_root_flag:
        sols.append(internalize(0))

    # Make a substitution for y = x^g, for g = gcd(a1, a2, ..., a_[n-1]) [if g > 1]
    # TODO Fractional power subs such as y = sqrt(x)?

    c_gcd = math.gcd(*coeffs.keys())

    if c_gcd > 1:
        coeffs = {
            pwr // c_gcd: coef
            for pwr, coef in coeffs.items()
        }

        degree //= c_gcd

        for sol in poly_solve_coeffs(degree, coeffs):
            sols.append(
                solve(Equals(var**c_gcd, sol), var).right
            )

        return sols

    # Otherwise solve normally
    for sol in poly_solve_coeffs(degree, coeffs):
        sols.append(sol)

    return sols


def is_poly(expr: DavidObject, var: Unknown):
    """Checks whether an expression is a polynomial with NUMERICAL powers."""

    terms = list(expr) if isinstance(expr, Operator) else [expr]

    poly_patterns = get_poly_patterns(var)

    for term in terms:
        matched = False

        # print('TERM', term)
        for pattern in poly_patterns:
            # print('   PATTERM', pattern.pattern)
            for match in pattern.match(term):
                # print('        match', match)

                # Not top level match
                if len(match[1]) != 0:
                    # print('invalid')
                    continue

                # print('valid match')
                matched = True
                break

            if matched:
                break

        if not matched:
            return False

    return True
