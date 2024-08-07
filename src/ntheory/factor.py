import itertools

from src.struct.number import Integer


def prime_factors(n: int | Integer):
    """Finds all the prime factors of a positive integer n."""

    # TODO Maybe a decorator
    if isinstance(n, Integer):
        n = n.value

    i = 2
    p_factors = {}

    # The smallest prime factor of a number cannot exceed n^2.
    #   Suppose n = pa, a > 1. Since p is the smallest prime factor, a >= p.
    #   This means that p = sqrt(n) when a = p, and otherwise is less than sqrt(n).
    while i * i <= n:

        # Divide out the prime factor until none are left.
        # It is guaranteed that i is prime if it divides n, since all the previous primes smaller than i
        # have already been factored out, which means that i cannot be composite.
        exp = 0
        while n % i == 0:
            n = n // i
            exp += 1

        if exp > 0:
            p_factors[i] = exp

        i += 1

    # If n is not 1, then it is prime, by the same logic that i is prime (all previous primes have been divided out).
    if n != 1:
        p_factors[n] = 1

    return p_factors


def factors(n: int | Integer):
    """Finds all the factors of a positive integer n."""

    if isinstance(n, Integer):
        n = n.value

    factors_l = []
    factors_r = []

    # Each factor i has a corresponding factor n // i. Hence, only all the factors less than sqrt(n) must be found.
    for i in range(1, int(n**(1/2)) + 1):
        if n % i == 0:
            factors_l.append(i)
            factors_r.append(n // i)

    # Skip sorting
    return factors_l + factors_r[::-1]
