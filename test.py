import time
from pprint import pprint

from src.manipulate.basic import *
from src.manipulate.eq import *
from src.manipulate.pattern import *
from src.core.visual import *
from src.manipulate.substitute import Identity, apply_greedily, make_sub, substitute
from src.struct.unknown import Wild
from src.struct.relation import Equals
from src.struct.number import *
from src.solve.solve import *
from src.manipulate.simplify import *

a, b, c, d = Unknown('a'), Unknown('b'), Unknown('c'), Unknown('d')
x, y, z = Unknown('x'), Unknown('y'), Unknown('z')
w = Wild('w')

# expr = x**3 * x + x*y*z**3 + (y + z)/x
# # expr = x + y + (x*z)
# expr2 = prep(expr)
#
# # print(tex(expr2))
# e = prep(1/x**(-1))
# print(tex(e))
# # print(tex(Multiply(-1,-1)))

# print(tex(x + y + z**((y + 1)**32)))


# from src.manipulate.hash import HashContext
#
# with HashContext() as i_hash:
#     print(i_hash(x + y + z))

p, q, r, s, t = Wild('p'), Wild('q'), Wild('r'), Wild('s'), Wild('t')
u, v = Wild('u', sequence=True), Wild('v', sequence=True)


# E = Add(Power(x, 2), Multiply(2, x, y), Power(y, 2), Power(x, 2), Multiply(2, x, x))
#
# P = Pattern(Add(Power(p, 2), Multiply(2, p, q), Power(q, 2)))
# P2 = Pattern(Power(Add(p, q), 2))
# print([p for p in P.match(E)])
# print(tex(E), ' = ')

# E = x**(absorb(y**z * 3)) + 3
# P = Pattern(p**(q*r) + r)

# E = x**2 + 2 * x * y + y**2 + z**2
#
# P1 = Pattern(p**2 + 2 * p * q + q**2)
# P2 = Pattern((p + q)**2)
#
# from src.manipulate.substitute import Identity, make_sub
# from src.solve.isolate import find_var
#
# I = Identity(P1, P2)
#
# print(make_sub(E, I))
#
# print(find_var(x**2 + y + z, x))

# P = Pattern(p * q, {p: lambda t: isinstance(t, Add)})
# E = (x + z) * (x + y)

# print([a for a in P.match(E)])

# import cProfile

# E = Equals(2*x + y, z + 5)
# # print(tex(E, frac=False))
# print(E)
# print('$$', tex(E, frac=False), '$$')

# def _test(pattern, test):
#     return tuple(m for m in Pattern(pattern).match(test))
#

# print(solve(Equals(2**(x+3), 16), x))

# homo, easy case
# print(homogenize((2**x)**2 + 3 * 2**x + 9, x))

# homo, hard case
# print([str(a) for a in solve(Equals(2**(2*x) + 2 * 2**x - 3, 0), x)])
# print(poly_solve(Add(9, Power(a, 2), Multiply(3, a)), a))
# print([str(a) for a in solve(Equals(e**(3*x) + 3*e**(-x), 4*e**x), x)])
# print([a for a in solve(Equals(x**2, 9))])

# print([tex(a) for a in solve_isolated(Equals((x + 1)**3, 9), 'left', (0, 0))])
# print(tex(Equals(Unknown('e')**(3*x) + 3*Unknown('e')**(-x), 4*Unknown('e')**x), frac=False))
# print(poly_solve(x**4 - 4*x**2 + 3, x)[0].eval(force=True), poly_solve(x**4 - 4*x**2 + 3, x)[1].eval(force=True))

def _test(pattern, test):
    return tuple(m for m in Pattern(pattern).match(test))

# print(eq_struct(a**3 + b**2, p**q + r**2))
# print(eq_struct(p*u, 3*x*y))

# X=Power(e, Multiply(ImaginaryUnit(), Power(3, -1)))
# print(X)
# print(p**(q/r))
# print([a for a in Pattern(p**(q/r)).match(X)])
# print([a for a in Pattern(1 * p).match(Power(e, Multiply(-1, -1, x)))])


# Pattern(u * var ** p).match(poly),
# Pattern(var ** p).match(poly),
# Pattern(u * var).match(poly),
# Pattern(var).match(poly)

# print([a for a in Pattern(u * x**p).match(x**4 - 4*x**2 + 3)])

# homo, different types together [y = x * 2**x]
# print(homogenize((x * 2**x)**2 + 3 * x * 2**x + 9, x))

# print([a for a in Pattern(p**(q*u)).match(2**(2*x))])

# E = Equals((x - 39)/3, x + 405)

# print(solve(E, x))

# print([a for a in Pattern(p/p).match(Multiply(Add(0, Multiply(78, -1)), Power(Add(Multiply(3, -1), 1), -1)))])
# print(interrogate({'p': Add(0, Multiply(78, -1))}, {'p': Add(Multiply(3, -1), 1)}, wilds=['p']))

# print([a for a in Pattern(u - u).match(Add(3*x, Multiply(66, -1), Multiply(-1, Add(Multiply(66, -1), 3*x))))])

# print(simplify(3 * (x - 22) - 3*(x - 22)))

# print(u - u)
# print([a for a in Pattern(u - u).match(Add(Multiply(3, -1, x), Multiply(3, x)))])

# collect_rules = IdentitySet(
#     Identity((x + p) * (x - p), x ** 2 - p ** 2),
#     Identity(u ** 2 + 2 * u * v + v ** 2, (u + v) ** 2, {u: lambda t: x in t.freq_table if isinstance(t, Operator) else eq_struct(t, x)}),
#
#     Identity(u * x + v * x, (u + v) * x),
#     Identity(x ** u * x ** v, x ** (u + v))
# )
#
# print(simplify(Add(Multiply(-3, x), Multiply(3, x))))

# print(make_sub(Add(Multiply(-3, x), Multiply(3, x)),     Identity(p, lambda n: Multiply(abs(n[p].value), Integer(-1)), {p: lambda t: isinstance(t, Number) and t.value < 0})))


# print(Add(2, Power(2, -1)).eval(force=True))


# print(apply_greedily((x + y)*(x - y), collect_rules, occ_metric))

# print(Pattern(p, {p: lambda t: eq_struct(t, x)}))

# poly = 5*x**2 + 6*x**2 + y*x + 2*z*x + 3 + x*x**2

# poly_c = poly_collect(poly, x)
# poly_s = poly_solve(Equals(poly_c, 0), x)
# print((x + y + (Number(3) + Number(4)) * z).eval())

# TODO make solve() not change the actual relation

# E = Equals(2*x - 5, x + 11)
# E = Equals(2 * x + 1, 3)
#
# S = solve(E, x)

# expr = a*x**2 + b*x**2 + c*x + 3*x + a**2*x + 5

# print(eq_struct(x+x+x+x+x+y+y, q+q+p+p+p+p+r))

# b = [a for a in Pattern(p**q + r).match(x**2 + y**2 + 1)]
# pprint(b)
# test = lambda pat, test: tuple((m[0], m[1], dict(m[2]) if m[2] is not None else m[2]) for m in Pattern(pat).match(test))
# pprint(test(p**q + r, x**2 + y**2 + 1))

# print([a for a in Pattern(p * u + p * v).match(x * y + x * y * z)])
# print([a for a in Pattern(p * v).match(x * y * z)])


# t0 = time.time()

# print(poly_collect(expr, x))

# print(make_sub(expr, Identity(p * q + p * r, p * (q + r))))
# asd = a*Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(x, 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1), 1)**2 + b*x**2 + c*x + 3*x + a**2*x + 5
# print([asd for asd in Pattern(p * q + p * r).match(a*x**2 + b*x**2 + c*x + 3*x + a**2*x + 5)])

# cProfile.run('Power(Power(Power(Power(Power(Power(Power(Power(Power(Power(b, 1), 1), 1), 1), 1), 1), 1), 1), 1), 1)')

# print([a for a in Pattern(p**1).match(asd)])
# t1=time.time()
# print(t1-t0)
# print(tex(E))
# print(tex(S, frac=False))
#
# print('$$', simplify(S.left), '$$')

# print(S.left, simplify(S.left))
# print(S.right, expand(S.left))

# print(Add(Multiply(0, 0), x).eval())


# print([a for a in Pattern(p * (q + r)).match(Multiply(1, Add(1, Multiply(1, x))))])

# print('$$', tex(S, frac=False), '$$')
# print('$$', tex(simplify(S.left), frac=False), '=', tex(expand(S.right), frac=False), '$$')


# E = 1**(Add(1, 2)) + Multiply(2, 1)
# P = Pattern(p**(2 + p) + 2*p)

# E = x**2 + 2*x*y + y**2 + z**2 +2*x*z + 3**(2*y*y+y**2+y**2)
# P = Pattern(p**2 + 2*p*q + q**2)

# E = x**2*y**0 + 2*x*y + y**2

# I = Identity(p**2 + 2*p*q + q**2, (p + q)**2)

# print([a for a in Pattern._match(P, x**(2 + y), p**(2 + p), parent=False)])

# E = x**(2 + y) + y + 2*x
# P = Pattern(p**(2 + p) + 2*p)

# E = x + y + z
# P = Pattern(p + q)

# print(E.freq_table)

# for m in P.match(E):
#     print(m)

from pprint import pp

# E = x + y + z
# print(Ex)

# v, offset, span = next(Pattern(p**0).match(Ex))
#
# subbed = substitute(Pattern(1), v)
#
# descend_struct(Ex, offset).terms = [subbed]
#
# print(Ex)
#
# print(subbed)

# simplify(Ex)

# print([a for a in Pattern(p**1).match(Ex)])

# from src.manipulate.simplify import ExpandIdentities, apply_until_constant


# S2 = simplify(x**2 * y**3 / y**4)
# print(S2)

# print(Power(p, -1))
# print(eq_struct(Power(2, -1), Power(p, -1)))

# print([a for a in Pattern(p/p).match(2 * x * Power(2, -1))])

# E2 = Add(Multiply(2, x), y, Multiply(y, -1))
# P2 = Pattern(p - p)
#
# print([a for a in P2.match(E2)])

# print([a for a in Pattern.gen_solutions(Add(y, Multiply(y, -1)), Add(p, Multiply(p, -1)), {'p': ((0,), (1, 0))}, [[{'p': y}], [{'p': y}]])])


# def substitute(pattern: Pattern, values: dict):
#     """Substitution function into the pattern."""
#
#     for wc, pos_list in pattern.wild_positions.items():
#
#         for pos in pos_list:
#
#             # TODO Find a better way. Seriously.
#             exec(
#                 'pattern.pattern' +
#                 ''.join(
#                     f'[{ n }]'
#                     for n in pos
#                 ) +
#                 ' = values[wc]'
#             )
#
#     return pattern
#
#
# for m in P.match(E):
#     replacement = substitute(P2, m[0]).pattern
#     Ec = E.duplicate(*E.terms)
#
#     for pos in m[1]:
#         p = pos.pop()
#
#         for j in range(len(m[1])):
#             if p in m[1][j]:
#                 m[1][j].remove(p)
#
#         Ec.terms[p[0]] = Number(0)
#
#     Ec += replacement
#     print(tex(absorb(Ec)), '=')

# P2 = p
# E2 = x
#
# # Power[y, 2] Power[[p], 2] {'p': [[0]], 'q': []} :    [({'p': y, 'q': None}, (0, 2))]
#
# print([a for a in Pattern._match(E2, P2, positions={'p': [[0]], 'q': []})])

# P = absorb(p**2 + 2 * p * q + q**2)
#
# E2 = Add(Power(y, Add(x, 1)), 1)
# P2 = Pattern(Add(Power(p, q + r), 1))

# [({'p': x, 'q': y}, ([1], [4])), ({'p': x, 'q': 2}, ([0], [4])), ({'p': y, 'q': Power[x, y]}, ([2], [4])), ({'p': x, 'q': y}, ([2], [4]))]
# [({'p': y, 'q': Power[x, y]}, ([2], [3])), ({'p': x, 'q': y}, ([2], [3])), ({'p': x, 'q': 2}, ([0], [3])), ({'p': x, 'q': y}, ([1], [3]))]

# print([p for p in P2.match(E2)])
