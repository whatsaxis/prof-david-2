from src.manipulate.eq import eq_struct
from src.manipulate.simplify import expand
from src.struct.unknown import Unknown

x, y, z, w = Unknown('x'), Unknown('y'), Unknown('z'), Unknown('w')


def assert_eq(actual, expected, msg=""):
    assert eq_struct(actual, expected), f"{msg}\n  got:      {actual}\n  expected: {expected}"


def assert_unchanged(fn, expr, msg=""):
    result = fn(expr)
    assert eq_struct(result, expr), f"{msg}\n  expected no change, got: {result}"


# =====================================================================
# EXPAND - common cases
# =====================================================================

def test_basic_distribution():
    result = expand(x * (y + z))
    assert_eq(result, x * y + x * z)


def test_distribution_other_operand_order():
    # Commutative multiplication - Add factor might be on either side.
    result = expand((y + z) * x)
    assert_eq(result, x * y + x * z)


def test_distribution_three_term_sum():
    result = expand(x * (y + z + w))
    assert_eq(result, x * y + x * z + x * w)


def test_no_distribution_without_add_factor():
    # x * y - neither factor is an Add, nothing should happen.
    assert_unchanged(expand, x * y, "x * y should not expand")


def test_distribution_leaves_stray_addend_alone():
    # Only the inner product should expand; w is untouched.
    result = expand(x * (y + z) + w)
    assert_eq(result, x * y + x * z + w)


# =====================================================================
# EXPAND - edge cases (lower confidence)
# =====================================================================

def test_expand_does_not_simplify_trailing_zero():
    result = expand(x * (y + 0))
    expected_unsimplified = x * y + x * 0
    assert_eq(result, expected_unsimplified,
               "expand() appears to also be simplifying - check whether "
               "ExpandIdentities and SimplifyIdentities are more coupled "
               "than expected")


def test_double_distribution_both_factors_are_sums():
    result = expand((x + y) * (z + w))

    full_foil = x * z + x * w + y * z + y * w
    partial = (x + y) * z + (x + y) * w

    assert eq_struct(result, full_foil) or eq_struct(result, partial), (
        f"Got a form matching neither expected shape: {result} - worth "
        f"inspecting directly, this is the most structurally complex case here."
    )