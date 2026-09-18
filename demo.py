"""
Demonstration
"""
from src.core.visual import tex
from src.manipulate.simplify import simplify
from src.solve.differentiate import differentiate
from src.solve.solve import solve
from src.struct.number import e
from src.struct.op import Log, Power, Sin
from src.struct.relation import Equals
from src.struct.unknown import Unknown

a, b, c, d = Unknown('a'), Unknown('b'), Unknown('c'), Unknown('d')
x, y, z = Unknown('x'), Unknown('y'), Unknown('z')

"""
Equation solving

3x + 7 = 19

x^2 - 5x + 6 = 0
x^10 (x + 1) = 0

e^(2x) - 4 e^x = -4
e^(3x) = 7

ln(x) = 3
"""

print(solve(Equals(
    3*x + 7,
    19
), x))

print(solve(Equals(
    x**2 - 5*x + 6,
    0
), x))

print(solve(Equals(
    x**10 * (x + 1),
    0
), x))

print(solve(Equals(
    e**(2*x) - 4 * e**x,
    -4
), x))

print(solve(Equals(
    e**(3*x),
    7
), x))

print(solve(Equals(
    Log(e, x),
    3
), x))

"""
Differentiation
"""

print(tex(differentiate(
    x**3 + 2 * x**2 - 5*x + 1,
    x
)))

print(tex(differentiate(
    x**2 * Sin(x),
    x
)))

print(tex(differentiate(
    e**x,
    x
)))

print(tex(differentiate(
    Log(e, x),
    x
)))

print(tex(differentiate(
    Sin(x**2),
    x
)))

print(tex(differentiate(
    x**(x**Power(2, -1)),
    x
)))
