"""
TODO:

2 modes of equality checking: deep, fast

eq() sorts both structures according to rules (if they are commutative) and directly compares them recursively.
No chance for collisions, much slower.

eq_fast() computes a hash for each term recursively and adds them up in a sort of hybrid commutative hash.
Collisions likely depending on use case, but does not rely on sorting. To be used in pattern matching.

Subset checks could possibly work with a second hash function that uses XOR. By comparing the hash of a commutative
structure, and applying the (self-reversing) operation to the pattern, it can be checked whether it is a subset.
VERY HIGH CHANCE OF COLLISIONS.

An easier way is to just use canonical representations - since the order of the terms is maintained, we can
check in O(n) [of the operator being checked] by simply iterating through and seeing if all elements are covered. They
will NOT be adjacent though, as there may be other terms between them.
"""

import collections

from src.core.base import DavidBase
from src.core.assume import Commutative, Symmetric
from src.struct.op import Log


def eq_type(a: DavidBase, b: DavidBase):
    """Checks whether two object instances are of the same type (i.e. same object, same assumptions)."""

    return type(a) is type(b) and a.assumptions == b.assumptions


def eq_struct(
        a,
        b,
        wild_conditions=None
):
    """
    Structural equality checking for algebraic objects with wilds. No ordering assumed.
    By design, does NOT confirm the semantics, only assessing the potential for a match.
    """

    from src.struct.op import Operator, Add, Multiply, Power, Log
    from src.struct.number import Number
    from src.struct.unknown import Unknown, Wild

    if wild_conditions is None:
        wild_conditions = {}

    # Basic type checks
    if isinstance(a, Wild) or isinstance(b, Wild):
        w, nw = a if isinstance(a, Wild) else b, b if isinstance(a, Wild) else a

        return wild_conditions.get(w, lambda _: True)(nw)

    # → Primitives
    if isinstance(a, Number):
        return hash(a) == hash(b)

    # → Type
    if not eq_type(a, b):
        return False

    # → Unknowns
    if isinstance(a, Unknown):
        return a.symbol == b.symbol

    # → Structures
    if isinstance(a, Operator):

        if not a.has_wilds and not b.has_wilds and len(a) != len(b):
            return False

        if a.has_wilds and b.has_wilds:
            raise Exception('Cannot compare Structures which both have Wild() as children!')

        # Not commutative? Just check all terms!
        if not a.ask(Commutative):
            # TODO Sequence (assumes associative?)

            if isinstance(a, Log):
                if not eq_struct(a.base, b.base):
                    return False

            for idx, a_el in enumerate(a):
                b_el = b[idx]

                # Uh oh, not equal!
                if not eq_struct(a_el, b_el):
                    return False

            return True

        # Commutative structures

        ws = a if a.has_wilds else b
        s = a if not a.has_wilds else b

        if len(s) < len(ws):
            return False

        cs = collections.Counter(s.freq_table)
        cws = collections.Counter(ws.freq_table)

        # Remove duplicates

        cs2 = cs.copy()
        cs2.subtract(cws)

        o_term_sum, w_term_sum, w_wild_sum = 0, 0, 0

        for k, v in cs2.items():
            # TODO We may want to rip off sympy and just do a cheap .is_wild thing... for everything
            if isinstance(k, Wild):
                w_term_sum += v

            if v < 0:
                w_term_sum += abs(v)
            elif v > 0:
                w_term_sum += v

        if not (a.has_wilds or b.has_wilds):
            return o_term_sum == w_term_sum == 0

        # TODO Goodness this is probably slow.. but at least it works every time
        def recurse_eq(wild_struct: Operator, cs_freq: collections.Counter):

            if len(wild_struct) == 0:
                return sum(cs_freq.values()) == 0

            w_term = wild_struct[0]

            if len(wild_struct) == 1 and isinstance(w_term, Wild) and w_term.sequence:
                return sum(cs_freq.values()) > 0

            for cs_term, freq in cs_freq.items():
                if freq == 0:
                    continue

                if not eq_struct(w_term, cs_term) or (isinstance(w_term, Wild) and w_term.sequence):
                    continue

                cs_freq_cpy = cs_freq.copy()
                cs_freq_cpy[cs_term] -= 1

                result = recurse_eq(wild_struct[1:], cs_freq_cpy)

                if result is True:
                    return True

            return False

        return recurse_eq(ws, cs)


# def eq_struct(a: DavidBase | Number | Unknown | Operator | Relation, b: DavidBase | Number | Unknown | Operator | Relation):
#     """Deep structural equality check (relies on sorting)."""
#
#     # TODO Move wild to unknown.py
#     from src.manipulate.pattern import Wild
#
#     a, b = internalize(a), internalize(b)
#
#     if isinstance(a, Wild) or isinstance(b, Wild):
#         return True
#
#     # → Basic checks
#     if type(a) is not type(b):
#         return False
#
#     # → Assumptions
#     if a.assumptions != b.assumptions:
#         return False
#
#     # → Numbers
#     if isinstance(a, Number):
#         # TODO Look at gcd() reduction for rationals.
#         return a.value == b.value
#
#     # → Unknowns
#     if isinstance(a, Unknown):
#         return a.symbol == b.symbol
#
#     # → Relations
#     if isinstance(a, Relation):
#         if a.ask(Symmetric):
#             return (eq_struct(a.left, b.left) and eq_struct(a.right, b.right)) or \
#                 (eq_struct(a.left, b.right) and eq_struct(a.right, b.left))
#
#         return eq_struct(a.left, b.left) and eq_struct(a.left, b.right)
#
#     # → Operators
#     if isinstance(a, Operator):
#         # if len(a) != len(b) or a.has_wilds != b.has_wilds:
#         #     return False
#
#         if a.ask(Commutative):
#             # TODO Yuck..
#             a, b = a.order_fast(), b.order_fast()
#
#         for t, i in enumerate(a):
#             if not eq_struct(t, b[i]):
#                 return False
#
#         return True


# def struct_hash(s: Operator | Unknown | Number):
#     """Returns a structural hash, ignoring their distinctness."""
#
#     from src.manipulate.pattern import Wild
#
#     if isinstance(s, Unknown | Wild):
#         return hash(Unknown)
#
#     if isinstance(s, Number):
#         return hash(Number)
#
#     sh = tuple(struct_hash(t) for t in s)
#
#     if s.ask(Commutative):
#         return sum(sh)
#
#     return hash(sh)
#
#
# def eq_struct_fast(a: Operator | Number | Relation, b: Operator | Number | Relation):
#     """Fast structural equality check (hash-based)."""
#
#     return hash(a) == hash(b)
