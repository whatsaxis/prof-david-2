from collections import defaultdict

from src.core.assume import assume, Commutative, Associative, Unary

from src.manipulate.eq import eq_type, eq_struct
from src.struct.op import internalize, Operator, Add, Multiply, Power
from src.struct.unknown import Unknown, Wild
from src.struct.number import Number


DavidObject = Operator | Unknown | Wild | Number


# def collect(op: Operator):
#     """Collects (structurally similar and constant) terms of a commutative structure."""
#
#     if not isinstance(op, Operator):
#         return op
#
#     # → Non-commutative structures
#     if not ask(op, Commutative):
#         return op.duplicate(*map(collect, op.terms))
#
#     # → Commutative structures
#     terms = defaultdict(lambda: 0)
#     constants = []
#
#     for term in op:
#         if isinstance(term, Real) and term.approximate is None:
#             continue
#
#         if isinstance(term, Number):
#             constants.append(term.value)
#
#         else:
#             terms[term] += 1
#
#     # → Symbolic terms
#     if isinstance(op, Add):
#         symbolic = op.duplicate(
#             *(
#                 Multiply(qty, collect(term))
#                 if qty != 1
#                 else collect(term)
#
#                 for term, qty in terms.items()
#             )
#         )
#     elif isinstance(op, Multiply):
#         symbolic = op.duplicate(
#             *(
#                 Power(collect(term), qty)
#                 if qty != 1
#                 else collect(term)
#
#                 for term, qty in terms.items()
#             )
#         )
#     else:
#         # TODO for custom structures?
#         symbolic = None
#
#     # → Constant terms; avoid prepending identity elements
#     if op.eval(*constants) != op.identity:
#         symbolic.terms = [op.eval(*constants)] + symbolic.terms
#
#     return absorb(symbolic)


# @assume(Commutative)
# def collect(op: Operator):
#     """Collects constant terms of a commutative structure [not recursive]."""
#
#     if not isinstance(op, Operator):
#         return op
#
#     terms = []
#     constants = []
#
#     for term in op:
#         if isinstance(term, Number):
#             constants.append(term)
#         else:
#             terms.append(collect(term))
#
#     if not eq_struct(op.eval(*constants), op.identity):
#         terms.append(op.eval(*constants))
#
#     return op.duplicate()


def absorb(op: Operator):
    """Absorbs associative operators of the same type as their parent."""

    if not isinstance(op, Operator):
        return op

    if op.is_absorbed:
        return op

    terms = []

    # TODO This optimization should work but REALLY messes up sometimes. I don't know why.
    # fr = op.freq_table.copy()

    for term in op:
        # fr[term] -= 1

        absorbed = absorb(term)

        if eq_type(term, op) and op.ask(Associative):

            terms += absorbed.terms
            # for a_term in absorbed.freq_table:
            #     fr[a_term] += absorbed.freq_table[a_term]

        else:
            # fr[absorbed] += 1
            terms.append(absorbed)

    # Reduce empty structures to their identities (e.g. Add[] -> 0)
    if len(terms) == 0:
        return op.identity

    # Expand out singular terms in a structure (e.g. Multiply[x] → x)
    if len(terms) == 1 and not op.ask(Unary):
        return terms[0]

    op.terms = terms

    return op.copy()


# def identity(op: Operator):
#     """Removes identity elements from operators."""
#
#     if isinstance(op, Add):
#         return absorb(op.duplicate(
#             *(
#                 identity(term)
#                 for term in op
#                 if not eq_struct(term, 0)
#             )
#         ))
#
#     if isinstance(op, Multiply):
#         terms = []
#
#         for term in op:
#             if eq_struct(term, 0):
#                 return internalize(0)
#
#             terms.append(identity(term))
#
#         return absorb(op.duplicate())
#
#     if isinstance(op, Power):
#         base, exp = op
#
#         if eq_struct(base, 0):
#             return internalize(0)
#
#         if eq_struct(exp, 1):
#             return identity(base)
#
#         if eq_struct(exp, 0):
#             return internalize(1)
#
#     return op


def prep(op: Operator | Unknown | Number):

    if isinstance(op, Unknown | Number):
        return op

    return absorb(op)
