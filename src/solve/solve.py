import math
import itertools
import collections

from src.core.base import DavidBase
from src.manipulate.basic import absorb
from src.manipulate.helpers import contains_var, descend_struct
from src.manipulate.simplify import ExpandIdentities, simplify
from src.ntheory.factor import factors
from src.struct.number import Integer, Number, e, pi, ImaginaryUnit

from src.struct.op import Log, Operator, internalize
from src.struct.unknown import Unknown
from src.struct.relation import Equals, Relation

from src.struct.op import Add, Multiply, Power
from src.struct.unknown import Wild

from src.manipulate.pattern import Pattern
from src.manipulate.substitute import Identity, IdentitySet, apply_greedily, apply_until_constant

from src.manipulate.eq import eq_struct


def find_var(op: DavidBase, var: Unknown, posn_offest=None):
    """Returns the positions of a variable in a structure."""

    if not posn_offest:
        posn_offest = []

    if not isinstance(op, Operator):
        if eq_struct(op, var):
            return [posn_offest]
        return []

    positions = []
    for i, t in enumerate(op):
        fv = find_var(t, var, posn_offest + [i])

        if fv:
            positions.extend(fv)

    return positions


def attract(eq: Relation, var: Unknown):
    """
    Attempts to attract and isolate terms containing a certain variable.
    TODO Uses specific factoring rewrite rules that reduce the total number of that variable in the relation.
    """

    # step 1: move everything to the left
    # step 2: try and bring stuff closer together with rewrite rules

    pass


def collect(eq: Operator | Unknown | Number, var: Unknown):
    """
    Uses specific rewrite rules to reduce the total number of occurrences of a variable in the relation.
    """

    lhs = apply_until_constant(eq, ExpandIdentities)

    def occ_metric(t):
        cnt = 0

        if isinstance(t, Unknown):
            # -1, so that branches with fewer variables are favoured
            return -1 if eq_struct(t, var) else 0

        elif isinstance(t, Operator):
            for term in t:
                cnt += occ_metric(term)

            return cnt

        else:
            return 0

    collect_rules = IdentitySet(
        Identity((var + p) * (var - p), var**2 - p**2),
        Identity(u**2 + 2*u*v + v**2, (u + v)**2, {u: lambda t: eq_struct(var, t) or var in t.freq_table}),

        Identity((u - v)*(u**2 + u*v + v**2), u**3 - v**3),
        Identity((u + v) * (u ** 2 - u*v + v ** 2), u ** 3 + v ** 3),

        Identity(u * var + v * var, (u + v) * var),
        Identity(var + var, 2 * var),
        Identity(var + u * var, (u + 1) * var),
        Identity(var**u * var**v, var**(u + v))
    )

    applied = apply_greedily(lhs, collect_rules, occ_metric)
    return applied[0], abs(applied[1])


def solve_isolated(rel: Relation, side: str, var_pos: tuple):
    """Solves for an isolated unknown by applying the inverse of each 'layer' surrounding it to both sides of a relation."""

    if side == 'right':
        rel = Equals(rel.right, rel.left)

    ref = rel.left

    sols = [rel]

    for p in var_pos:
        sols_next = []

        for s in sols:
            rel_cpy = s.copy()

            if isinstance(ref, Add):
                rtc = ref.terms.copy()
                rtc.pop(p)

                minus = ref.duplicate(*rtc)
                rel_cpy.add(-minus)
            elif isinstance(ref, Multiply):
                rtc = ref.terms.copy()
                rtc.pop(p)

                div = ref.duplicate(*rtc)
                rel_cpy.div(div)
            elif isinstance(ref, Power):
                # If term is base
                if p == 0:
                    # Take root
                    # TODO Complex roots

                    rel_cpy.pow(1 / ref[1])

                    if isinstance(ref[1], Number) and isinstance(ref[1].value, int) and ref[1].value > 0:
                        for k in range(1, ref[1].value + 1):
                            sols_next.append(Equals(rel.left, e**(pi * ImaginaryUnit() * k / ref[1]) * rel.right))

                # If term is exponent
                elif p == 1:
                    rel_cpy.log(ref[0])

            sols_next.append(rel_cpy)

        sols = sols_next
        ref = ref[p]

    # TODO check for domain of functions

    return tuple(
        simplify(s.right).eval()
        for s in sols
    )


p, q, r, s = Wild('p'), Wild('q'), Wild('r'), Wild('s')
u, v = Wild('u', sequence=True), Wild('v', sequence=True)


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


def get_coefficients(expr: Add, var: Unknown):
    poly = poly_collect(expr, var)

    terms = [pt for pt in itertools.chain(
        Pattern(u * var**p).match(poly),
        Pattern(var**p).match(poly),
        Pattern(u * var).match(poly),
        Pattern(var).match(poly)
    )]

    poly_term_indices = set(
        pt[1][0]
        for pt in terms

        # Only top-level matches
        if len(pt[1]) == 1
    )

    degree = 0
    non_var = []

    for i, t in enumerate(poly):
        if i not in poly_term_indices:
            non_var.append(t)

    coefficients = {0: absorb(Add(*non_var))}

    for t in terms:
        # Only top-level matches
        if len(t[1]) > 1:
            continue

        coef, exp = t[0].get('u', internalize(1)), t[0].get('p', internalize(1))

        # TODO Non-numeric powers and coefficients?

        if exp.value > degree:
            degree = exp.value

        coefficients[exp.value] = coef

    return degree, coefficients


def poly_solve_coeffs(degree: int, coeffs: dict):
    """Solves a polynomial given coefficients."""

    if degree == 1:
        a, b = coeffs.get(1), coeffs.get(0, internalize(0))

        return -b / a,

    if degree == 2:

        a, b, c = coeffs.get(2), coeffs.get(1, internalize(0)), coeffs.get(0, internalize(0))

        delta = b**2 - 4*a*c
        return (-b + delta**Power(2, -1)) / 2, (-b - delta**Power(2, -1)) / (2*a)

    # if degree == 3:
    #     a, b, c, d = coeffs.get(3), coeffs.get(2, internalize(0)), coeffs.get(1, internalize(0)), coeffs.get(0, internalize(0))
    #
    #     delta_0 = b**2 - 3*a*c
    #     delta_1 = 2*b**3 - 9*a*b*c + 27*a**2*d
    #
    #     C1 = delta_1 +


def poly_eliminate_negative_powers(poly: Add, var: Unknown):
    """Multiplies out negative powers, increasing the degree of the polynomial by the smallest negative degree."""

    degree, coeffs = get_coefficients(poly, var)

    # Deal with negative powers
    # TODO Non-numeric powers?
    if any(p < 0 for p in coeffs.keys()):
        min_neg_pow = min(coeffs.keys())

        poly_2 = []
        for pt in poly:
            poly_2.append(pt * var**abs(min_neg_pow))

        return simplify(poly.duplicate(*poly_2))

    return poly


def poly_solve(poly: Add, var: Unknown):
    """
    | Solves a polynomial equation of the form a_1 x^b_1 + a_2 x^b_2 + ... + a_n = 0.
    | Note that the polynomial is assumed to be on the left.
    | Also assumed that poly_eliminate_negative_powers() has been called on the polynomial already.
    """

    degree, coeffs = get_coefficients(poly, var)

    # Check for multiples in the coefficients

    # TODO Non-numeric coefficients and powers

    zero_root_flag = False
    # TODO zero root flag

    # Factor out the maximum variable power

    if eq_struct(coeffs.get(0, internalize(0)), internalize(0)):
        p_min = min(coeffs.keys(), key=lambda p: not eq_struct(coeffs[p], internalize(0)))

        coeffs = {
            pwr: coef - p_min
            for pwr, coef in coeffs.keys()
        }

        zero_root_flag = True
        degree -= p_min

    # Make a substitution for y = x^g, for g = gcd(a1, a2, ..., a_[n-1]) [if g > 1]

    c_gcd = math.gcd(*coeffs.keys())

    if c_gcd > 1:
        coeffs = {
            pwr // c_gcd: coef
            for pwr, coef in coeffs.items()
        }

        degree //= c_gcd

        sols = []
        for sol in poly_solve_coeffs(degree, coeffs):
            sols.append(
                solve(Equals(var**c_gcd, sol), var).right
            )

        return sols

    # Otherwise solve normally

    return poly_solve_coeffs(degree, coeffs)


def get_term_type(expr: Operator | Unknown | Number, var: Unknown):
    """Returns the classification of an expression with relation to a variable."""

    # todo

    # if isinstance(expr, Number):
    #     return 'constant',
    # if isinstance(expr, Unknown):
    #     if eq_struct(expr, var):
    #         return 'linear',
    #     return 'constant',
    #
    # for pos in find_var(expr, var):
    #     if isinstance(descend_struct(expr, pos[:-1]))


def is_poly(expr: Operator, var: Unknown):
    """Checks whether an expression is a polynomial."""

    for pos in find_var(expr, var):
        if len(pos) == 2 or (len(pos) == 3 and pos[-1] == 0 and isinstance(descend_struct(expr, pos[:-1] + [1]), Integer)):
            continue
        else:
            return False

    return True


def largest_sub_struct_containing_var(expr: Operator, var: Unknown):
    """Finds the largest sub-structure containing a variable for homogenization."""

    # Equivalent to finding the largest shared prefix after a find_var() call

    var_posns = find_var(expr, var)

    if not var_posns:
        return None, None

    current_prefix = 0

    # len(var_posns[0]) - 1 so that it targets the encompassing structure and not just the variable
    while all(vp[:current_prefix] == var_posns[0][:current_prefix] for vp in var_posns) and current_prefix < len(var_posns[0]) - 1:
        current_prefix += 1

    pos = var_posns[0][:current_prefix]
    return pos, descend_struct(expr, pos).copy()


def homogenize(expr: Add, var: Unknown, *, sub_idx=0):
    """
    | Attempts to find a substitution in a variable to transform an expression into a polynomial.
    | Called after ``expand()`` and ``poly_collect()``.
    """

    expr = expr.copy()

    if not isinstance(expr, Add):
        return expr

    ExpSplitIdentities = IdentitySet(
        Identity(p ** (q + u), p ** q * p ** u),
        Identity(p ** (q * u), (p ** q) ** u, {q: lambda t: contains_var(t, var)})
    )

    LogSplitIdentities = IdentitySet(
        Identity(Log(p, q*u), Log(p, q) + Log(p, u)),
        Identity(Log(p, q**r), r * Log(p, q))
    )

    split = apply_until_constant(apply_until_constant(expr, ExpSplitIdentities, do_eval=False), LogSplitIdentities, do_eval=False)
    # print('split', split)

    sub = None
    for i, term in enumerate(split):
        local_sub_pos, sub_possibility = largest_sub_struct_containing_var(term, var)

        # Non-variable term
        if sub_possibility is None:
            continue

        # print('----------------------')
        # print('term', term)
        # print('pos', local_sub_pos)
        # print('sub', sub, sub_possibility)
        # print('descended', descend_struct(split, [i] + local_sub_pos[:-1])[local_sub_pos[-1]])

        if sub is None:
            sub = sub_possibility
        else:
            if not eq_struct(sub, sub_possibility):
                return None, None

        # TODO Somehow create new sub variable letters
        uk = Unknown(f's_{ sub_idx }')

        # Within the term
        if local_sub_pos:
            descend_struct(split, [i] + local_sub_pos[:-1])[local_sub_pos[-1]] = uk
        # The term itself
        else:
            split[i] = uk

    return (uk, sub), split

    # Get largest term of x's from the first term in expr
    # TODO

    # Check if it contains exp or log or trig (if not exit because why.. or maybe not. could be more convenient... ayyyy idk)
    # TODO

    # Sub array (only append here if no instances of the variable remain in the structure)
    # TODO


def solve(rel: Relation, var: Unknown, *, sub_idx=0):
    """Solves for a variable."""

    print('►►► Equation solver')
    print('      for ', rel)

    rel_cpy = rel.copy()

    var_positions_l = find_var(rel_cpy.left, var)
    var_positions_r = find_var(rel_cpy.right, var)

    isolated = len(var_positions_l + var_positions_r) == 1

    print('    → Checking for isolated equation')
    if isolated:
        print(f'        → Solving isolated equation for { var }:')
        print('              ', rel_cpy)

        if var_positions_l:
            side = 'left'
            var_pos = var_positions_l[0]
        else:
            side = 'right'
            var_pos = var_positions_r[0]

        return solve_isolated(rel_cpy, side, var_pos)

    else:
        print(f'    → Solving non-isolated equation ({ len(var_positions_l + var_positions_r) } variable instances)')

        # [Movement] Move all terms to the left side

        rel_cpy.add(-rel_cpy.right)
        print('        → Moved all terms to left side')

        # [Simplification] The solver simplifies the expression with select rewrite rules.
        rel_cpy = Equals(simplify(rel_cpy.left), 0)

        print('        → Performed simplification')
        print('              ', rel_cpy)

        # [Collection] The solver attempts to reduce the number of the desired unknown by applying a set of patterns.
        lhs, num_vars = collect(rel_cpy.left, var)
        rel_cpy = Equals(lhs, rel_cpy.right)

        print(f'        → Performed collection ({ num_vars } remaining variable instances)')
        print('              ', rel_cpy)

        if num_vars == 1:
            return solve(rel_cpy, var)

        # [PolySolve] Solver attempts to solve as a polynomial.

        print('        → Invoking PolySolve')

        if is_poly(rel_cpy.left, var):
            print(f'        → Expression is a polynomial!')
            print(f'        → Eliminating negative powers')
            rel_cpy = Equals(
                simplify(poly_eliminate_negative_powers(rel_cpy.left, var)),
                rel_cpy.right
            )

            print(f'        → Solving { rel_cpy } with PolySolve')
            sols = poly_solve(rel_cpy.left, var)

            if sols:
                return sols
            else:
                print('        → Expression is not solvable (yet... degree > 3)')
        else:
            print('        → Expression is not a polynomial')

        # [Homogenization] Solver attempts to make a substitution in the variable to transform the equation into a polynomial.

        print(f'        → Attempting homogenization')
        sub, homo = homogenize(rel_cpy.left, var, sub_idx=sub_idx)

        if sub is not None and homo is not None:
            print(f'        → Substitution found!')
            print('              ', sub[0], '=', sub[1], '  in')
            print('              ', homo)

            sols = solve(Equals(homo, 0), sub[0], sub_idx=sub_idx + 1)

            if sols is None:
                print(f'[↑]     → No solutions found.')
                return None

            print(f'[↑]     → Solutions found after substitution!')

            for sol in sols:
                print('              ', sub[0], '=', sol.eval(force=True))

            # Todo check if there are actually solutions returned

            print(f'        → Solving above equations for ', sub[0], '=', sub[1])
            return tuple(
                solve(Equals(sub[1], sol.eval(force=True)), var, sub_idx=sub_idx + 1)
                for sol in sols
            )
        else:
            print(f'        → No suitable substitution found.')

        # [Attraction] The solver tries to bring terms closer by applying rewrite rules according to a distance metric.
        pass
