import collections

from src.core.assume import Commutative
from src.core.base import DavidBase
from src.struct.number import Number
from src.struct.op import Operator
from src.struct.unknown import Unknown, Wild


def eq_type(a: DavidBase, b: DavidBase):
    """Checks whether two object instances are of the same type (i.e. same object, same assumptions)."""

    return type(a) is type(b) and a.assumptions == b.assumptions


def _eq_struct_non_commutative(
        a,
        b,
        wild_conditions,
        eq_struct
):
    # TODO Sequence (assumes associative? not that deep rn since we only have powers basically lol)

    for idx, a_el in enumerate(a):
        b_el = b[idx]

        # Uh oh, not equal!
        if not eq_struct(a_el, b_el, wild_conditions):
            return False

    return True


def _bipartite_match_feasible(remaining_terms: list, remaining_cs: 'collections.Counter', wild_conditions, eq_struct):
    if not remaining_terms:
        # TODO what
        # All ambiguous terms placed - whatever's left in remaining_cs is handled by the caller
        return True, remaining_cs

    term, rest = remaining_terms[0], remaining_terms[1:]

    # A backtracking algorithm with a reduced search space to assess the potential for a match
    for cs_term, freq in remaining_cs.items():
        if freq <= 0:
            continue
        if not eq_struct(term, cs_term, wild_conditions=wild_conditions):
            continue

        branch_cs = remaining_cs.copy()
        branch_cs[cs_term] -= 1

        ok, result_cs = _bipartite_match_feasible(rest, branch_cs, wild_conditions, eq_struct)
        if ok:
            return True, result_cs
        # else: this candidate didn't lead anywhere, try the next one

    return False, None


def _eq_struct_commutative(
        a,
        b,
        wild_conditions,
        eq_struct
):

    ws = a if a.has_wilds else b
    s = a if not a.has_wilds else b

    if len(s) < len(ws):
        return False

    concrete_terms = []
    ambiguous_terms = []
    unconstrained_wilds = 0
    sequence_wilds = 0

    for term in ws:
        # Sequence variables
        if isinstance(term, Wild) and term.sequence:
            sequence_wilds += 1
        elif isinstance(term, Wild):
            # Wild with constraints
            if term in wild_conditions:
                ambiguous_terms.append(term)

            # Wild that can match anything
            else:
                unconstrained_wilds += 1

        # Wild-containing terms (handled recursively
        elif isinstance(term, Operator) and term.has_wilds:
            ambiguous_terms.append(term)

        # Number, Unknown, or a wildcard-free Operator
        else:
            concrete_terms.append(term)

    # --- 1: cancel non-wild terms directly -------------------------
    cs = collections.Counter(s.freq_table)

    for term in concrete_terms:
        if cs[term] <= 0:
            return False
        cs[term] -= 1

    # --- 2: real matching for the ambiguous residual only ----------
    if ambiguous_terms:
        ok, cs = _bipartite_match_feasible(ambiguous_terms, cs, wild_conditions, eq_struct)
        if not ok:
            return False

    # --- 3: unconstrained wilds just need enough terms left --------
    remaining_total = sum(v for v in cs.values() if v > 0)

    if sequence_wilds == 0:
        return remaining_total == unconstrained_wilds
    else:
        # So that there are no empty sequence variables
        return remaining_total >= unconstrained_wilds + sequence_wilds


def eq_struct(
        a,
        b,
        wild_conditions=None
):
    """za
    Structural equality checking for algebraic objects with wilds. No ordering assumed.
    By design, does NOT confirm the semantics, only assessing the potential for a match.
    Either 0, or 1, but not both of the parameters can contain wilds.
    """


    if wild_conditions is None:
        wild_conditions = {}

    # Basic type checks
    if isinstance(a, Wild) or isinstance(b, Wild):
        w, nw = a if isinstance(a, Wild) else b, b if isinstance(a, Wild) else a

        if isinstance(nw, Wild) or (isinstance(nw, Operator) and nw.has_wilds):
            raise Exception('Cannot compare Wild() to an Operator containing Wild()')

        return wild_conditions.get(w, lambda _: True)(nw)

    # TODO I don't particularly like this. Makes below redundant too but ok.
    if isinstance(a, Operator) and isinstance(b, Operator) and a.has_wilds and b.has_wilds:
        raise Exception('Cannot compare operators which both have Wild() as children')

    # → Type
    if not eq_type(a, b):
        return False

    # → Primitives
    if isinstance(a, Number):
        return a == b

    # → Unknowns
    if isinstance(a, Unknown):
        return a.symbol == b.symbol

    # → Structures
    if isinstance(a, Operator):
        if not a.has_wilds and not b.has_wilds and len(a) != len(b):
            return False

        if a.has_wilds and b.has_wilds:
            raise Exception('Cannot compare operators which both have Wild() as children')

        if not a.ask(Commutative):
            return _eq_struct_non_commutative(a, b, wild_conditions, eq_struct)
        else:
            return _eq_struct_commutative(a, b, wild_conditions, eq_struct)

    return False

# print(cs, cws)
#
# # Remove duplicates for commutative structures
#
# cs2 = cs.copy()
# cs2.subtract(cws)
#
# for cs_term, freq in cs2.items():
#     # If there are any -ve terms from cws that are not wilds
#     # then the two structures cannot possibly be equal
#     if freq < 0 and not isinstance(cs_term, Wild):
#         return False
#
# # Otherwise, we have a counter of some number of remaining terms from the non-wild structure
# # and some wild-containing terms
#
#
#
# # TODO Goodness this is probably slow.. but at least it works every time
# def recurse_eq(wild_struct: Operator, cs_freq: collections.Counter):
#
#     if len(wild_struct) == 0:
#         return sum(cs_freq.values()) == 0
#
#     w_term = wild_struct[0]
#
#     if len(wild_struct) == 1 and isinstance(w_term, Wild) and w_term.sequence:
#         return sum(cs_freq.values()) > 0
#
#     for cs_term, freq in cs_freq.items():
#         if freq == 0:
#             continue
#
#         if not eq_struct(w_term, cs_term) or (isinstance(w_term, Wild) and w_term.sequence):
#             continue
#
#         cs_freq_cpy = cs_freq.copy()
#         cs_freq_cpy[cs_term] -= 1
#
#         # TODO Do this with indices to be more efficient
#         result = recurse_eq(wild_struct[1:], cs_freq_cpy)
#
#         if result is True:
#             return True
#
#     return False
#
# return recurse_eq(ws, cs)



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
