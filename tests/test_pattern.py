from src.struct.unknown import Unknown, Wild
from src.manipulate.pattern import Pattern
from src.struct.number import Number

x, y, z = Unknown('x'), Unknown('y'), Unknown('z')
p, q, r, s, t = Wild('p'), Wild('q'), Wild('r'), Wild('s'), Wild('t')
u, v = Wild('u', sequence=True), Wild('v', sequence=True)


def _test(pattern, test):
    return tuple(m for m in Pattern(pattern).match(test))


def test_basic():

    # Non-operator

    # Yes, this is expected behaviour. The matcher will only return a match where information is extracted, and won't just confirm a match.
    assert _test(x, x) == ()
    assert _test(x, y) == ()
    assert _test(x, x + y) == ()

    assert _test(p, x) == (({'p': x}, (), None),)

    # TODO Hmm would be nice if instead of (0,) it gave the frequency dict... for non-op patterns
    assert _test(p, x + y) == (({'p': x + y}, (), None), ({'p': x}, (0,), None), ({'p': y}, (1,), None),)
    assert _test(u, x + y + z) == (({'u': x + y + z}, (), None), ({'u': x}, (0,), None), ({'u': y}, (1,), None), ({'u': z}, (2,), None))

    # Commutative

    assert _test(p + q, x + y) == (({'p': x, 'q': y}, (), {x: 0, y: 0}), ({'p': y, 'q': x}, (), {x: 0, y: 0}))
    assert _test(p + 1, x + y + 1) == (({'p': x}, (), {x: 0, y: 1, Number(1): 0}), ({'p': y}, (), {x: 1, y: 0, Number(1): 0}))

    # Non-commutative

    assert _test(p**2, x**2) == (({'p': x}, (), (0, 2)),)
    assert _test(p**q, x**y) == (({'p': x, 'q': y}, (), (0, 2)),)


def test_differing_commutativity():

    assert _test(p**q + r, x**2 + y**2 + 1) == (
        ({'p': y, 'q': Number(2), 'r': x**2}, (), {x**2: 0, y**2: 0, Number(1): 1}),
        ({'p': x, 'q': Number(2), 'r': y**2}, (), {x**2: 0, y**2: 0, Number(1): 1}),
        ({'p': x, 'q': Number(2), 'r': Number(1)}, (), {x**2: 0, y**2: 1, Number(1): 0}),
        ({'p': y, 'q': Number(2), 'r': Number(1)}, (), {x**2: 1, y**2: 0, Number(1): 0}),
    )

    # Nested, differing commutativity

    assert _test(p**(q + r) + s, x**(y**(z + 1) + 5) + 7) == (
        ({'p': x, 'q': y**(z + 1), 'r': Number(5), 's': Number(7)}, (), {x**(y**(z + 1) + 5): 0, Number(7): 0}),
        ({'p': x, 'q': Number(5), 'r': y**(z + 1), 's': Number(7)}, (), {x**(y**(z + 1) + 5): 0, Number(7): 0}),
        ({'p': y, 'q': z, 'r': Number(1), 's': Number(5)}, (0, 1), {y**(z + 1): 0, Number(5): 0}),
        ({'p': y, 'q': Number(1), 'r': z, 's': Number(5)}, (0, 1), {y**(z + 1): 0, Number(5): 0})
    )


def test_complex():
    # Complex patterns
    assert _test(p**(q*r) + r, x**(3 * y**z) + 3) == (
        ({'p': x, 'q': y**z, 'r': 3}, (), {x**(3 * y**z): 0, Number(3): 0}),
    )

    assert _test(p + 2*q, x**2 + 2*x*y + y**(3 + 2*z)) == (
        ({'p': Number(3), 'q': z}, (2, 1), {Number(3): 0, 2*z: 0}),
    )


def test_sequence():
    # TODO

    assert _test(p**(q*u), 5**(x*y*z)) == (
        ({'p': Number(5), 'q': x, 'u': y*z}, (), (0, 2)),
        ({'p': Number(5), 'q': y, 'u': x*z}, (), (0, 2)),
        ({'p': Number(5), 'q': z, 'u': x*y}, (), (0, 2))
    )

    assert _test(p*u + p*v, x*y + x*y*z) == (
        ({'p': x, 'u': y, 'v': y*z}, (), {x*y: 0, x*y*z: 0}),
        ({'p': y, 'u': x, 'v': x*z}, (), {x * y: 0, x * y * z: 0}),
        ({'p': x, 'u': y*z, 'v': y}, (), {x * y: 0, x * y * z: 0}),
        ({'p': y, 'u': x*z, 'v': x}, (), {x * y: 0, x * y * z: 0})
    )


def test_edge():

    assert _test(p, 0) == (({'p': 0}, (), None),)

    assert _test(1, 1) == ()
    assert _test(1, 2) == ()

    assert _test(p + q, 0) == ()
    assert _test(p * q, x + y) == ()
    assert _test(p + q + r, x + y) == ()
