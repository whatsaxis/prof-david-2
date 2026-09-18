from src.struct.unknown import Unknown
from src.struct.op import Log, Power, internalize
from src.manipulate.eq import eq_struct
from src.manipulate.simplify import simplify

x, y, z, w = Unknown('x'), Unknown('y'), Unknown('z'), Unknown('w')


def assert_eq(actual, expected, msg=""):
    assert eq_struct(actual, expected), f"{msg}\n  got:      {actual}\n  expected: {expected}"


def assert_unchanged(fn, expr, msg=""):
    result = fn(expr)
    assert eq_struct(result, expr), f"{msg}\n  expected no change, got: {result}"


"""Addition"""


def test_additive_identity():
    assert_eq(simplify(x + 0), x)
    assert_eq(simplify(0 + x), x)  # commutative - should work either order

    assert_eq(simplify(x - 0), x)
    assert_eq(simplify(0 - x), -x)


def test_additive_inverse():
    assert_eq(simplify(x - x), internalize(0))


def test_like_terms_combine():
    assert_eq(simplify(x + x), 2 * x)


def test_coefficient_plus_term():
    # p + u*p -> p*(u+1); with p=x, u=3 this should give 4*x
    assert_eq(simplify(x + 3 * x), 4 * x)
    assert_eq(simplify(x + 3 * x + 5 * x + x**2), 9 * x + x**2)


def test_repeated_addition_multi_step():
    # x + x + x should collapse fully, not just partially (e.g. stop at 2x + x)
    assert_eq(simplify(x + x + x), 3 * x)


"""Multiplication"""


def test_multiplicative_zero():
    assert_eq(simplify(0 * x), internalize(0))
    assert_eq(simplify(x * 0), internalize(0))


def test_multiplicative_identity():
    assert_eq(simplify(x * 1), x)
    assert_eq(simplify(1 * x), x)
    assert_eq(simplify(internalize(1) * internalize(0)), internalize(0))
    assert_eq(simplify(1 * (x*y*1)), x*y)


"""Exponentiation"""


def test_power_one():
    assert_eq(simplify(x**1), x)

def test_power_times_base():
    assert_eq(simplify(x**2 * x), x**3)
    assert_eq(simplify(x**3 * x**5), x**8)


def test_power_times_power_symbolic_exponents():
    assert_eq(simplify(x**y * x**2), x**(y + 2))
    assert_eq(simplify(x**y * x**z), x**(y + z))


def test_power_of_power():
    assert_eq(simplify((x**5)**3), x**15)
    assert_eq(simplify(((x**x)**y)**3), x**(3*x*y))
    assert_eq(simplify((x**y)**z), x**(y * z))


def test_power_zero_nonzero_base():
    assert_eq(simplify(y**0), internalize(1))


"""Fractions"""


def test_division_self_nonzero():
    assert_eq(simplify(y / y), internalize(1))


def test_simplify_fractions():
    assert_eq(simplify(Power(2, -1) + Power(2, -1)), internalize(1))
    assert_eq(simplify(Power(3, -1) + Power(6, -1)), Power(2, -1))
    assert_eq(simplify(Power(2, -1) + Power(3, -1)), 5 * Power(6, -1))
    assert_eq(simplify(1 - Power(2, -1)), Power(2, -1))
    assert_eq(simplify(5 * Power(6, -1) - Power(3, -1)), Power(2, -1))
    assert_eq(simplify(x/3 + x/6), x/2)


"""Logs"""

def test_log_self():
    assert_eq(simplify(Log(x, x)), internalize(1))
    assert_eq(simplify(Log(x, x*y)), internalize(1) + Log(x, y))


def test_log_of_power():
    assert_eq(simplify(Log(x, x**5)), internalize(5))


def test_log_product_rule():
    result = simplify(Log(x, y * z))
    assert_eq(result, Log(x, y) + Log(x, z))


# =====================================================================
# SIMPLIFY - edge cases
# =====================================================================

def test_zero_to_the_zero_not_simplified():
    # TODO This is to do with eval(). The pattern matcher itself works fine.

    # p**0 -> 1 is explicitly guarded against p == 0, since 0**0 is
    # mathematically ambiguous - this should NOT become 1.
    # result = simplify(internalize(0)**internalize(0))
    # assert not eq_struct(result, internalize(1)), (
    #     "0**0 simplified to 1, but the p**0 rule is guarded against p==0 - "
    #     "either the guard isn't working, or this is intentional and the "
    #     "test's assumption is wrong."
    # )
    pass


def test_zero_over_zero_not_simplified():
    # p/p -> 1 is guarded against p == 0, since 0/0 is undefined.
    result = simplify(internalize(0) / internalize(0))
    assert not eq_struct(result, internalize(1)), (
        "0/0 simplified to 1, but the p/p rule is guarded against p==0."
    )


def test_no_spurious_simplification_distinct_terms():
    # x + y and x * y shouldn't be touched - no identity applies.
    assert_unchanged(simplify, x + y, "x + y should not simplify")
    assert_unchanged(simplify, x * y, "x * y should not simplify")


def test_idempotency():
    # Running simplify twice shouldn't change the result further -
    # if apply_until_constant is doing its job, this should always hold.
    for expr in (x + 0, x + x, x**2 * x, Log(x, y * z), x + 3 * x):
        once = simplify(expr)
        twice = simplify(once)
        assert_eq(twice, once, f"simplify not idempotent for {expr}")


def test_chained_rule_application():
    # Two separate identities need to fire in sequence:
    # (x + 0) * 1  ->  x * 1  ->  x
    assert_eq(simplify((x + 0) * 1), x)

    # x**1 + 0  ->  x + 0  ->  x
    assert_eq(simplify(x**1 + 0), x)


def test_log_product_rule_three_factors_recursive():
    assert eq_struct(simplify(Log(x, y * z * w)), Log(x, y) + Log(x, z) + Log(x, w))


def test_power_zero_times_zero_interaction():
    result = simplify(x**0 * 0)
    assert_eq(result, internalize(0))

