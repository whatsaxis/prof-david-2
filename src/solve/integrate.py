from src.manipulate.basic import DavidObject, absorb
from src.manipulate.eq import eq_struct
from src.manipulate.helpers import contains_var, descend_struct
from src.manipulate.pattern import Pattern
from src.manipulate.simplify import simplify
from src.manipulate.substitute import Identity, IdentitySet, apply_one, apply_until_constant, find_subs_identity, \
    make_sub
from src.solve.differentiate import differentiate
from src.solve.polynomial import find_struct, find_var
from src.solve.solve import solve, solve_isolated
from src.struct.number import e, minus_one
from src.struct.op import Add, Cos, Log, Multiply, Power, Sin, internalize
from src.struct.relation import Equals
from src.struct.unknown import Unknown, Wild

p, q, r = Wild('p'), Wild('q'), Wild('r')
u, v = Wild('u', sequence=True), Wild('v', sequence=True)

# TODO VERY WIP


def find_candidate_u_subs(expr: DavidObject, var: Unknown, *, give_locations=False):
    """
    Finds potentially useful candidate structures for integration substitutions.

    e.g. find_useful_int_structures(2*x * Sin(x**2), x) --> {x, x**2, Sin(x**2)}
    """

    locations = find_var(expr, var)

    if not give_locations:
        possibilities = set()
    else:
        possibilities = []

    # For each location, traverse its tree and use that structure as a possible substitution
    for loc in locations:
        loc = tuple(loc)

        for i in range(len(loc)):
            pos = loc[:i + 1]
            struct = descend_struct(expr, pos)

            if not give_locations:
                possibilities.add(struct)
            else:
                possibilities.append((descend_struct(expr, pos), pos))

    return possibilities


def find_candidate_ibp(expr: DavidObject, var: Unknown, *, give_locations=False):
    """
    Finds potentially useful candidate structures for integration substitutions.

    e.g. find_useful_int_structures(2*x * Sin(x**2), x) --> {x, x**2, Sin(x**2)}
    """

    locations = find_var(expr, var)

    if not give_locations:
        possibilities = set()
    else:
        possibilities = []

    # For each location, traverse its tree and use that structure as a possible substitution
    for loc in locations:
        loc = tuple(loc)

        for i in range(len(loc)):
            pos = loc[:i + 1]
            struct = descend_struct(expr, pos)

            if not give_locations:
                possibilities.add(struct)
            else:
                possibilities.append((descend_struct(expr, pos), pos))

    return possibilities


def integrate(expr: DavidObject, var: Unknown):
    """Indefinite integral of an expression."""

    # Split addition into many integrals that we add
    if isinstance(expr, Add):
        result = Add()

        for term in expr:
            result.append(integrate(term, var))

        return absorb(result)

    def contains_no_var(t):
        return not contains_var(t, var)

    # # Remove constant terms if multiplication
    # constant_terms = []
    # if isinstance(expr, Multiply):
    #     for term in expr:
    #         pass

    # Base case: basic integrals
    BasicIntegrals = IdentitySet(

        # TODO Have sequence variables not match any too?
        # Power rule
        Identity(u, u * var, {u: contains_no_var}),
        Identity(p, Power(2, -1) * var**2, {p: lambda t: eq_struct(t, var)}),
        Identity(u * var, u * Power(2, -1) * var**2, {u: contains_no_var}),
        Identity(var**p, 1/(p + 1) * var**(p + 1), {p: lambda t: not eq_struct(t, minus_one)}),
        Identity(u * var**p, u/(p + 1) * var**(p + 1), {u: contains_no_var, p: lambda t: not eq_struct(t, minus_one)}),
        Identity((u * var) ** p, u**p / (p + 1) * var ** (p + 1),
                 {u: contains_no_var, p: lambda t: not eq_struct(t, minus_one)}),

        # Trigonometry
        Identity(Sin(var), -Cos(var)),
        Identity(Cos(var), Sin(var)),
        Identity(Sin(v * var), -1 / v * Cos(v * var), {v: contains_no_var}),
        Identity(Cos(v * var), 1 / v * Sin(v * var), {v: contains_no_var}),
        Identity(u * Sin(var), -u * Cos(var), {u: contains_no_var}),
        Identity(u * Cos(var), u * Sin(var), {u: contains_no_var}),
        Identity(u * Sin(v * var), -u/v * Cos(v * var), {u: contains_no_var, v: contains_no_var}),
        Identity(u * Cos(v * var), u / v * Sin(v * var), {u: contains_no_var, v: contains_no_var}),

        # Log
        Identity(p/var, p * Log(e, var), {p: contains_no_var})

        # Exponents
        # TODO e^(ax)
    )

    print('INTEGRATING', expr, 'wrt', var)

    changed, result = apply_one(expr, BasicIntegrals, top_level=True, return_changed=True)

    # Integral was solved by a basic case above
    if changed:
        return result

    if isinstance(expr, Multiply):
        # Otherwise, try u-sub (direct ones... it's not the best)
        for u_for_x in find_candidate_u_subs(expr, var):
            print('CAN SUB', u_for_x)
            du_dx = simplify(differentiate(u_for_x, var))
            print('du = ', du_dx, 'dx')

            # print(find_struct(expr, du_dx), expr, du_dx)

            # TODO Erm lol
            for _, pos, freq in Pattern(du_dx).match(expr):
                sub_var = Unknown('u', 'sub')

                # Top-level match for [...] dx = du
                if pos == tuple():
                    print('SUB FOUND')
                    print('u =', u_for_x)
                    print('du/dx =', du_dx)

                    # Replace the du/dx * dx with du
                    int_du = make_sub(expr.copy(), internalize(1), pos, freq)

                    print('integral as du:', int_du)

                    # Solve for x in terms of u
                    x_for_u = solve(Equals(sub_var, u_for_x), var)[0]
                    print('x =', x_for_u)
                    x_for_u = simplify(x_for_u)

                    # Replace all instances of x in terms of u
                    int_u_du = int_du.copy()

                    for _, var_pos, var_freq in Pattern(var).match(int_du):
                        int_u_du = make_sub(int_u_du, x_for_u, var_pos, var_freq)

                    print('after subbing u:', int_u_du)
                    int_u_du = simplify(int_u_du)
                    print('after simplify:', int_u_du)

                    # Integrate after the u-sub
                    antideriv_u = integrate(int_u_du, sub_var)

                    antideriv_x = antideriv_u.copy()
                    print(antideriv_x)

                    # Sub u back for x
                    for _, var_pos, var_freq in Pattern(sub_var).match(antideriv_u):
                        print(antideriv_x, u_for_x, var_pos, var_freq)
                        antideriv_x = make_sub(antideriv_x, u_for_x, var_pos, var_freq)

                    print('b4', antideriv_x)
                    antideriv_x = simplify(antideriv_x)
                    return antideriv_x


    # TODO Partial fractions

    # TODO IBP
