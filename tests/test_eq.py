import pytest
import collections

from src.struct.unknown import Unknown, Wild
from src.struct.number import Number
from src.manipulate.eq import eq_struct

x, y, z = Unknown('x'), Unknown('y'), Unknown('z')
p, q, r, s = Wild('p'), Wild('q'), Wild('r'), Wild('s')
u, v = Wild('u', sequence=True), Wild('v', sequence=True)


# TODO These need to be expanded a bit

def test_primitives():
    assert eq_struct(Number(1), Number(1)) is True
    assert eq_struct(Number(1), Number(2)) is False


def test_unknowns():
    assert eq_struct(x, x) is True
    assert eq_struct(x, y) is False


def test_wild_matches_anything_by_default():
    assert eq_struct(p, x) is True
    assert eq_struct(p, x + y) is True
    assert eq_struct(x, p) is True  # Order shouldn't matter


def test_wild_conditions_restrict_matching():
    conditions = {p: lambda term: isinstance(term, Number)}

    assert eq_struct(p, Number(5), wild_conditions=conditions) is True
    assert eq_struct(p, x, wild_conditions=conditions) is False


def test_both_wilds_raises():
    with pytest.raises(Exception):
        eq_struct(p, q)  # Can't test wild vs wild

    with pytest.raises(Exception):
        eq_struct(p, x ** q)  # Can't test wild vs wild in operator

    with pytest.raises(Exception):
        eq_struct(p + x, y ** q)  # Can't test wild vs wild in operator

    with pytest.raises(Exception):
        eq_struct(p + q, r + s)  # Can't test two wild operators


def test_non_commutative_strict_order():
    assert eq_struct(x**2, x**2) is True
    assert eq_struct(x**y, x**2) is False
    assert eq_struct(x**y, y**x) is False  # Order matters


def test_non_commutative_with_wild():
    assert eq_struct(p**2, x**2) is True
    assert eq_struct(p**q, x**y) is True
    assert eq_struct(p**2, x**3) is False  # Order matters (again)


def test_commutative_no_wilds_order_independent():
    assert eq_struct(x + y + z, z + y + x) is True
    assert eq_struct(x + y, x + z) is False
    assert eq_struct(x + y, x + y + z) is False  # Different term count


def test_commutative_with_wild_sufficiency():
    assert eq_struct(p + q, x + y) is True
    assert eq_struct(p + q + r, x + y) is False  # Not enough terms for 3 wilds


def test_sequence_wild_terminal():
    # sequence wild absorbing everything, single-term pattern
    assert eq_struct(u, x + y + z) is True
    assert eq_struct(u, x) is True
    assert eq_struct(p + u, x) is False


def test_sequence_wild_non_terminal_known_gap():
    assert eq_struct(p + u + q, x + y + z + 1) is True


def test_backtrack():
    assert eq_struct(p**2 + x**2, x**2 + y**2) is True
