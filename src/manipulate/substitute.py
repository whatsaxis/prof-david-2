from typing import Callable

from src.struct.op import Operator, internalize

from src.manipulate.basic import DavidObject, absorb

from src.manipulate.pattern import Pattern
from src.manipulate.helpers import descend_struct, from_freq
from src.struct.unknown import Wild


class Identity:
    def __init__(self, a: DavidObject, b: DavidObject | Callable, wild_conditions=None):
        a, b = internalize(a), internalize(b)

        self.a = Pattern(a, wild_conditions)
        self.b = Pattern(b, wild_conditions) if isinstance(b, DavidObject) else b


class IdentitySet:
    def __init__(self, *identities: Identity):
        self.identities = identities

    def __add__(self, other: 'IdentitySet'):
        return IdentitySet(*(self.identities + other.identities))

    def __iter__(self):
        return iter(self.identities)


def substitute(pattern: Pattern, values: dict):
    """Substitution function into the pattern."""

    if not isinstance(pattern.pattern, Operator):
        if isinstance(pattern.pattern, Wild):
            return values[pattern.pattern]

        return pattern.pattern

    p_terms = pattern.pattern.copy()

    for wc, pos_list in pattern.wild_positions.items():

        for pos in pos_list:

            # TODO Find a better way. Seriously.
            exec(
                'p_terms' +
                ''.join(
                    f'[{ n }]'
                    for n in pos
                ) +
                ' = values[wc]'
            )

    return p_terms


# TODO A little inefficient that we only pick the match object of each match call but ok

def make_sub(test: Operator, identity: Identity, *, depth=1):
    """Depth can be set to ``True`` to get all possible substitutions."""

    # TODO Reverse, how do we deal with functions?

    pattern = identity.a
    sub_pattern = identity.b

    # pattern = identity.b if reverse else identity.a
    # sub_pattern = identity.a if reverse else identity.b

    it = pattern.match(test)

    subs = []

    while depth is True or depth > 0:

        try:
            var_subs, posn_offset, term_info = next(it)
            cpy = test.copy()

            # Make substitution

            if isinstance(sub_pattern, Callable):
                subbed = sub_pattern(var_subs)
            else:
                subbed = substitute(sub_pattern, var_subs)

            # Construct new structure

            ref_sub = descend_struct(cpy, posn_offset)

            # Non-commutative
            if isinstance(term_info, tuple):
                ref_sub.terms = [*ref_sub[:term_info[0]], subbed, *ref_sub[term_info[1] + 1:]]

            # Non-operator
            elif term_info is None:
                ref_sub = descend_struct(cpy, posn_offset[:-1])
                el_idx = posn_offset[-1]

                ref_sub[el_idx] = subbed

            # Commutative
            else:
                ref_sub.terms = from_freq(term_info) + [subbed]

            subs.append(cpy)

            depth -= 1
        except StopIteration:
            return subs

    return subs


def apply_until_constant(op: Operator, i_set: IdentitySet, *, do_eval=True):
    """Applies identity rules of an identity set until no more can be applied."""

    op_copy = op.copy()
    print(op)

    # TODO Make this for Identity() objects too instead of only IdentitySet()s

    while True:
        changed = False
        prev_hash = hash(op_copy)

        for i in i_set:
            options = make_sub(op_copy, i)

            if not options:
                continue

            # print('---------', i.a.pattern, i.a.wild_conditions)
            # print('    op now:', op_copy)
            # print('    op after:', options[0])

            # TODO Not a fan of absorb()ing; the substitution should just replace the original term instead of its insides
            # TODO But i guess not that big a deal since we have a function for it already and it would be better than copying code (sleep on it)
            # TODO Plus we can just eval without an if statement here lol
            op_copy = absorb(options[0])

        # TODO Can i eval here
        if do_eval:
            op_copy = op_copy.eval(force=False)

        if hash(op_copy) != prev_hash:
            changed = True

        if not changed:
            break

    return op_copy


def apply_greedily(op: Operator, i_set: IdentitySet, metric: Callable, *, depth=10):
    """Applies identities of an identity set according to a certain metric."""

    # TODO No evaluation here

    op_copy = op.copy()
    op_score = metric(op_copy)

    best_branch = None
    best_score = 0

    for i in i_set:
        options = make_sub(op_copy, i)

        if not options:
            if best_branch is None or op_score > best_score:
                best_branch = op
                best_score = op_score

            continue

        branch = options[0]
        score = metric(branch)

        if depth == 0:
            if best_branch is None or score > best_score:
                best_branch = branch
                best_score = score
        else:
            best_deep, best_deep_score = apply_greedily(branch, i_set, metric, depth=depth - 1)

            if best_branch is None or best_deep_score > best_score:
                best_branch = best_deep
                best_score = best_deep_score

    return best_branch, best_score


def apply_to_depth(op: Operator, i_set: IdentitySet, *, depth=8, do_eval=True):
    """Applies an identity set wherever possible, returning all branches after a certain depth [max of len(i_set)^depth branches]."""

    pass
