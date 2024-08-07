import math

from src.manipulate.eq import eq_struct
from src.manipulate.substitute import Identity, IdentitySet, apply_until_constant
from src.manipulate.basic import absorb
from src.struct.op import Log, Multiply, Operator, internalize
from src.struct.unknown import Wild
from src.struct.number import Integer, Number, Real

from src.struct.op import Add


p, q, r = Wild('p'), Wild('q'), Wild('r')
u, v = Wild('u', sequence=True), Wild('v', sequence=True)


def distributive(wild_values):
    pv: Add = wild_values[p]
    qv = wild_values[q]

    o = []

    for t in pv:
        o.append(t * qv)

    return pv.duplicate(*o)


def binomial(wild_values):
    add: Add = wild_values[p]
    power = wild_values[q]

    o = []

    add1 = absorb(add.duplicate(*add[:len(add) // 2]))
    add2 = absorb(add.duplicate(*add[len(add) // 2:]))

    for i in range(0, power.value + 1):
        c = math.comb(power.value, i)
        o.append(c * add1**i * add2**(power - i))

    add.duplicate(*o)

    return add.duplicate(*o)


ExpandIdentities = IdentitySet(
    Identity(p * q, distributive, {p: lambda m: isinstance(m, Add)}),
    # Identity(p**q, binomial, {p: lambda m: isinstance(m, Add), q: lambda m: isinstance(m, Integer) and m.value > 0})
)

FactorIdentities = IdentitySet(
    Identity(p * p, p**2),
    Identity(p**q * p, p**(q + 1)),
    Identity(p ** q * p ** r, p ** (q + r)),

    # Identity(p * q + p * r, p * (q + r)),
    Identity(p + p, 2 * p),
    Identity(q * p + p, (q + 1) * p)
)

SimplifyIdentities = IdentitySet(
    Identity(p, lambda n: Multiply(abs(n[p].value), Integer(-1)), {p: lambda t: isinstance(t, Real | Integer) and t.value < 0 and t.value != -1}),

    # Addition
    Identity(p + 0, p),
    Identity(u - u, 0),
    Identity(p + p, 2*p),
    Identity(p + u*p, p*(u + 1)),

    # Multiplication
    Identity(1 * p, p),
    Identity(0 * p, 0),
    Identity(p**q * p, p**(q + 1)),
    Identity(p**q * p**r, p**(q + r)),
    Identity((p**q)**r, p**(q*r)),
    # Identity(p * q, distributive, {p: lambda t: isinstance(t, Add)}),

    # Exponentiation
    Identity(p**1, p),
    Identity(p**0, 1, {p: lambda t: not eq_struct(t, internalize(0))}),
    Identity(p / p, 1, {p: lambda t: not eq_struct(t, internalize(0))}),

    # Logarithms
    Identity(Log(p, p), 1),
    Identity(Log(p, p**q), q),
    Identity(Log(p, q * u), Log(p, q) + Log(p, u))
)


def expand(op: Operator):
    """Expanding."""

    return apply_until_constant(op, ExpandIdentities)


def simplify(op: Operator):
    """Simplification."""

    return apply_until_constant(op, SimplifyIdentities)
