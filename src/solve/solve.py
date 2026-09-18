from src.manipulate.basic import absorb
from src.manipulate.evaluate import evaluate
from src.manipulate.helpers import contains_var, descend_struct
from src.manipulate.simplify import ExpandIdentities, simplify
from src.solve.polynomial import find_var, get_poly_coefficients, is_poly, poly_solve
from src.struct.number import ImaginaryUnit, Number, e, pi

from src.struct.op import Log, Operator
from src.struct.unknown import Unknown
from src.struct.relation import Equals, Relation

from src.struct.op import Add, Multiply, Power
from src.struct.unknown import Wild

from src.manipulate.substitute import Identity, IdentitySet, apply_greedily, apply_until_constant

from src.manipulate.eq import eq_struct


p, q, r, s = Wild('p'), Wild('q'), Wild('r'), Wild('s')
u, v = Wild('u', sequence=True), Wild('v', sequence=True)


def attract(eq: Relation, var: Unknown):
    """
    Attempts to attract and isolate terms containing a certain variable.
    TODO Uses specific factoring rewrite rules that reduce the total number of that variable in the relation.
    """

    # step 1: move everything to the left
    lhs = absorb(eq.left - eq.right)

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
        Identity(u**2 + 2*u*v + v**2, (u + v)**2, {u: lambda t: eq_struct(var, t) or (isinstance(t, Operator) and var in t.freq_table)}),

        Identity((u - v)*(u**2 + u*v + v**2), u**3 - v**3, {u: lambda t: eq_struct(var, t) or (isinstance(t, Operator) and var in t.freq_table)}),
        Identity((u + v) * (u ** 2 - u*v + v ** 2), u ** 3 + v ** 3, {u: lambda t: eq_struct(var, t) or (isinstance(t, Operator) and var in t.freq_table)}),

        Identity(u * var + v * var, (u + v) * var),
        Identity(var + var, 2 * var),
        Identity(var + u * var, (u + 1) * var),
        Identity(var**u * var**v, var**(u + v))
    )

    applied = apply_greedily(lhs, collect_rules, occ_metric)

    collected = simplify(applied[0])
    instances = len(find_var(collected, var))

    return collected, instances


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

                    rel_cpy.pow(1 / ref[1])

                    # TODO Complex roots
                    # if isinstance(ref[1], Number) and isinstance(ref[1].value, int) and ref[1].value > 0:
                    #     for k in range(1, ref[1].value + 1):
                    #         sols_next.append(Equals(rel.left, e**(pi * ImaginaryUnit() * k / ref[1]) * rel.right))

                # If term is exponent
                elif p == 1:
                    rel_cpy.log(ref[0])
            elif isinstance(ref, Log):
                rel_cpy.log_pow(ref.base)

            sols_next.append(rel_cpy)

        sols = sols_next
        ref = ref[p]

    # TODO check for domain of functions

    return tuple(
        evaluate(simplify(s.right))
        for s in sols
    )


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
        return None, expr

    SplitIdentities = IdentitySet(
        # Power splitting
        Identity(p ** (q + u), p ** q * p ** u),
        Identity(p ** (q * u), (p ** q) ** u,
                 {q: lambda t: contains_var(t, var), u: lambda t: not contains_var(t, var)}),

        # Log splitting
        Identity(Log(p, q * u), Log(p, q) + Log(p, u)),
        Identity(Log(p, q ** r), r * Log(p, q))
    )

    split = apply_until_constant(expr, SplitIdentities, do_eval=False)
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
        # print('descended', descend_struct(split, (i,) + local_sub_pos[:-1])[local_sub_pos[-1]])

        if sub is None:
            sub = sub_possibility
        else:
            if not eq_struct(sub, sub_possibility):
                return None, None

        uk = Unknown(f's', str(sub_idx))

        # Within the term
        if local_sub_pos:
            descend_struct(split, (i,) + local_sub_pos[:-1])[local_sub_pos[-1]] = uk
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


def solve(rel: Relation, var: Unknown, *, sub_idx=0, verbose=False):
    """Solves for a variable."""

    def vprint(*s):
        if verbose:
            print(*s)

    vprint('►►► Equation solver')
    vprint('      for ', rel)

    rel_cpy = rel.copy()

    var_positions_l = find_var(rel_cpy.left, var)
    var_positions_r = find_var(rel_cpy.right, var)

    isolated = len(var_positions_l + var_positions_r) == 1

    vprint('    → Checking for isolated equation')
    if isolated:
        vprint(f'        → Solving isolated equation for { var }:')
        vprint('              ', rel_cpy)

        if var_positions_l:
            side = 'left'
            var_pos = var_positions_l[0]
        else:
            side = 'right'
            var_pos = var_positions_r[0]

        return solve_isolated(rel_cpy, side, var_pos)

    else:
        vprint(f'    → Solving non-isolated equation ({ len(var_positions_l + var_positions_r) } variable instances)')

        # [Movement] Move all terms to the left side

        rel_cpy.add(-rel_cpy.right)
        vprint('        → Moved all terms to left side')

        # [Simplification] The solver simplifies the expression with select rewrite rules.
        rel_cpy = Equals(simplify(rel_cpy.left), 0)

        vprint('        → Performed simplification')
        vprint('              ', rel_cpy)

        # [Collection] The solver attempts to reduce the number of the desired unknown by applying a set of patterns.
        lhs, num_vars = collect(rel_cpy.left, var)
        rel_cpy = Equals(lhs, rel_cpy.right)

        vprint(f'        → Performed collection ({ num_vars } remaining variable instances)')
        vprint('              ', rel_cpy)

        if num_vars == 1:
            return solve(rel_cpy, var)

        # [PolySolve] Solver attempts to solve as a polynomial.

        vprint('        → Invoking PolySolve')

        if is_poly(rel_cpy.left, var):
            vprint(f'        → Expression is a polynomial!')

            # todo jesus christ
            # rel_cpy = Equals(
            #     simplify(poly_eliminate_negative_powers(evaluate(rel_cpy.left, force=True), var)),
            #     rel_cpy.right
            # )

            degree, coeffs = get_poly_coefficients(evaluate(rel_cpy.left, force=True), var)

            vprint(f'        → Solving { rel_cpy } with PolySolve')
            sols = tuple(simplify(s) for s in poly_solve(degree, coeffs, var, verbose=verbose))

            if sols:
                return sols
            else:
                vprint('        → Expression is not solvable (yet... degree > 3)')
        else:
            vprint('        → Expression is not a polynomial')

        # [Homogenization] Solver attempts to make a substitution in the variable to transform the equation into a polynomial.

        vprint(f'        → Attempting homogenization')
        sub, homo = homogenize(rel_cpy.left, var, sub_idx=sub_idx)

        if sub is not None and homo is not None:
            vprint(f'        → Substitution found!')
            vprint('              ', sub[0], '=', sub[1], '  in')
            vprint('              ', homo)

            sols = solve(Equals(homo, 0), sub[0], sub_idx=sub_idx + 1)

            if sols is None:
                vprint(f'[↑]     → No solutions found.')
                return None

            vprint(f'[↑]     → Solutions found after substitution!')

            for sol in sols:
                vprint('              ', sub[0], '=', evaluate(sol))

            # Todo check if there are actually solutions returned

            vprint(f'        → Solving above equations for ', sub[0], '=', sub[1])

            all_sols = tuple()
            for sol in sols:
                # Solve equation for substitution for each solution of original eqn to get back variable
                all_sols += solve(Equals(sub[1], evaluate(sol)), var, sub_idx=sub_idx + 1)

            return all_sols
        else:
            vprint(f'        → No suitable substitution found.')

        # [Attraction] The solver tries to bring terms closer by applying rewrite rules according to a distance metric.
        pass
