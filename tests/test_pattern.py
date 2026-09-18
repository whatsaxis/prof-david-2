import pytest

from src.struct.op import internalize
from src.struct.unknown import Unknown, Wild
from src.manipulate.pattern import Pattern, interrogate
from src.struct.number import Number

x, y, z = Unknown('x'), Unknown('y'), Unknown('z')
p, q, r, s, t = Wild('p'), Wild('q'), Wild('r'), Wild('s'), Wild('t')
u, v = Wild('u', sequence=True), Wild('v', sequence=True)


def _test(pattern, test):
    return tuple(m for m in Pattern(pattern).match(test))


def test_basic():

    # Non-operator

    # Yes, this is expected behaviour. The matcher will only return a match where information is extracted, and won't just confirm a match.
    assert _test(x, x) == (({}, (), None),)
    assert _test(x, y) == ()
    assert _test(x, x + y) == (({}, (0,), None),)

    assert _test(p, x) == (({'p': x}, (), None),)

    # TODO Hmm would be nice if instead of (0,) it gave the frequency dict... for non-op patterns
    assert _test(p, x + y) == (({'p': x + y}, (), None), ({'p': x}, (0,), None), ({'p': y}, (1,), None),)
    assert _test(u, x + y + z) == (({'u': x + y + z}, (), None),)

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

    # The point is to engineer identities so that they do one thing at a time, many times
    # For example here, factor 1 term out, which can be repeated many times to factor many terms out
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


def test_bare_wild_matches_whole_subtree():
    # p can bind to the ENTIRE structure, not just a leaf.
    result = _test(p, x + y)
    assert ({'p': x + y}, (), None) in result


def test_bare_wild_also_matches_at_every_subterm():
    # parent=True recursion means p is also tried against each child.
    result = _test(p, x + y)
    assert ({'p': x}, (0,), None) in result
    assert ({'p': y}, (1,), None) in result


def test_wild_condition_restricts_bare_wild_match():
    conditions = {p: lambda term: isinstance(term, Number)}
    pat = Pattern(p, wild_conditions=conditions)

    assert tuple(pat.match(Number(5))) != ()
    assert tuple(pat.match(x)) == ()


def test_non_commutative_concrete_terms_no_wilds():
    assert _test(x, x) == (({}, (), None),)
    assert _test(x, y) == ()
    assert _test(x, 2*y**x) == (({}, (1, 1), None),)

    assert _test(x**2, x**2) == (({}, (), (0, 2)),)  # exact structural match exists somewhere
    assert _test(x**2, x**3 + x**2 + 5*x + 9*(7 + x**2)) == (
            ({}, (1,), (0, 2)),
            ({}, (3, 1, 1), (0, 2))
    )
    assert _test(1 - x, (1 - x)**2 + y*(1 - x)) == (
            ({}, (0, 0), {internalize(1): 0, -x: 0}),
            ({}, (1, 1), {internalize(1): 0, -x: 0}),
    )
    assert _test(1 - x, y**(y + 1 - x)) == (
            ({}, (1,), {internalize(1): 0, -x: 0, y: 1}),
    )
    assert _test(y**2, x**2) == ()  # mismatched base


def test_non_commutative_single_wild():
    assert _test(p**2, x**2) == (({'p': x}, (), (0, 2)),)


def test_non_commutative_multiple_wilds():
    assert _test(p**q, x**y) == (({'p': x, 'q': y}, (), (0, 2)),)


def test_non_commutative_mismatched_exponent_fails():
    assert _test(p**2, x**3) == ()


def test_commutative_two_wilds_both_orderings():
    result = _test(p + q, x + y)
    assert ({'p': x, 'q': y}, (), {x: 0, y: 0}) in result
    assert ({'p': y, 'q': x}, (), {x: 0, y: 0}) in result
    assert len(result) == 2


def test_commutative_wild_plus_constant():
    result = _test(p + 1, x + y + 1)
    assert ({'p': x}, (), {x: 0, y: 1, Number(1): 0}) in result
    assert ({'p': y}, (), {x: 1, y: 0, Number(1): 0}) in result


def test_commutative_too_many_wilds_for_available_terms():
    # p + q + r needs 3 slots, x + y only has 2 - should yield nothing.
    assert _test(p + q + r, x + y) == ()


def test_nested_differing_commutativity():
    # Power (non-commutative) nested inside Add (commutative).
    result = _test(p**q + r, x**2 + y**2 + 1)
    assert len(result) == 4
    assert ({'p': x, 'q': Number(2), 'r': y**2}, (), {x**2: 0, y**2: 0, Number(1): 1}) in result


# ---------------------------------------------------------------------------
# Testing optimization 1: repeated wildcard within one pattern
# ---------------------------------------------------------------------------

def test_repeated_wildcard_basic_binding_consistency():
    # p appears twice - both occurrences MUST bind to the same value.
    # x + x + y: p should be able to bind to x (matching both x's),
    # consuming them both, leaving y for q.
    result = _test(p + p + q, x + x + y)

    for bindings, *_ in result:
        # Whatever p is bound to, it must be internally consistent -
        # there is only one 'p' key, so this is trivially true by
        # construction, but the SHAPE of results (duplicates or not)
        # is what we're actually checking below.
        assert bindings['p'] == x
        assert bindings['q'] == y


def test_repeated_wildcard_does_not_duplicate_yield():
    result = _test(p + p + q, x + x + y)
    unique_bindings = {frozenset(b.items()) for b, *_ in result}

    assert len(result) == len(unique_bindings), (
        'Got duplicate yields for the same binding.'
    )


def test_repeated_wildcard_no_valid_binding():
    # p appears twice but there's only ONE x available - should fail
    # to find any binding for p (nothing left over means no q either
    # if p can't be satisfied twice).
    assert _test(p + p, x + y) == ()


# ---------------------------------------------------------------------------
# Sequence wilds
# ---------------------------------------------------------------------------

def test_sequence_wild_absorbs_everything_single_term_pattern():
    # TODO Hmm I need to think about what behaviour I want here.
    assert _test(u, x + y + z) == (({'u': x + y + z}, (), None),)


def test_sequence_wild_within_larger_pattern():
    result = _test(p**(q * u), 5**(x * y * z))
    assert ({'p': Number(5), 'q': x, 'u': y * z}, (), (0, 2)) in result
    assert ({'p': Number(5), 'q': y, 'u': x * z}, (), (0, 2)) in result
    assert ({'p': Number(5), 'q': z, 'u': x * y}, (), (0, 2)) in result
    assert len(result) == 3


def test_multiple_sequence_wilds():
    result = _test(p * u + p * v, x * y + x * y * z)
    assert len(result) == 4
    assert ({'p': x, 'u': y, 'v': y * z}, (), {x * y: 0, x * y * z: 0}) in result


def test_sequence_wild_duplicate_subterm_in_bundle():
    try:
        result = _test(p * u + p * v, x * y + x * y * x)
    except Exception as e:
        pytest.fail(f'Matching raised unexpectedly: {e!r}')

    # Whatever comes back, every yielded binding should be well-formed:
    for bindings, *_ in result:
        assert 'p' in bindings and 'u' in bindings and 'v' in bindings


def test_sequence_wild_insufficient_terms():
    # If constant/wild terms in the pattern eat everything, the sequence
    # wild should get nothing left to absorb -> no match for that branch.
    result = _test(p + q + r + u, x + y)
    assert result == ()


# ---------------------------------------------------------------------------
# Testing interrogate()
# ---------------------------------------------------------------------------

def test_interrogate_merges_non_conflicting_facts():
    fact_a = {p: x}
    fact_b = {q: y}
    merged = interrogate(fact_a, fact_b, wilds=[p, q])
    assert merged[p] == x
    assert merged[q] == y


def test_interrogate_detects_contradiction():
    fact_a = {p: x}
    fact_b = {p: y}
    assert interrogate(fact_a, fact_b, wilds=[p]) is False


def test_interrogate_ignores_missing_wildcard():
    fact_a = {p: x}
    fact_b = {}
    merged = interrogate(fact_a, fact_b, wilds=[p, q])
    assert merged[p] == x
    assert merged[q] is None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_bare_wild_against_zero():
    assert _test(p, internalize(0)) == (({'p': internalize(0)}, (), None),)


def test_two_literals_equal_yields_nothing():
    assert _test(internalize(1), internalize(1)) == (({}, (), None),)


def test_two_literals_unequal_yields_nothing():
    assert _test(internalize(1), internalize(2)) == ()


def test_wild_sum_against_zero_yields_nothing():
    assert _test(p + q, internalize(0)) == ()


def test_wild_product_against_sum_wrong_operator():
    assert _test(p * q, x + y) == ()


def test_pattern_needs_more_terms_than_available():
    assert _test(p + q + r, x + y) == ()
