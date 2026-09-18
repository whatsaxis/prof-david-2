from typing import Callable

from src.manipulate.eq import eq_struct
from src.manipulate.evaluate import evaluate
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


def sub_into_pattern(pattern: Pattern, values: dict):
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


def make_sub(struct: DavidObject, subbed: DavidObject, posn_offset: tuple, term_info: dict | tuple | None):
    """Makes a substitution of a pattern populated with values into a certain position of another structure."""

    # Commutative
    if isinstance(term_info, dict):
        ref_sub = descend_struct(struct, posn_offset)
        ref_sub.terms = from_freq(term_info) + [subbed]

        # TODO: Is this redundant when operator is top level?
        struct._regenerate_freq(recurse=True)

    # Non-commutative
    elif isinstance(term_info, tuple):
        ref_sub = descend_struct(struct, posn_offset)
        ref_sub.terms = [*ref_sub[:term_info[0]], subbed, *ref_sub[term_info[1] + 1:]]

        # OLD BUG: When ref_sub was updated, it did not update the frequency table of the parent struct.
        # That is very, very bad!
        struct._regenerate_freq(recurse=True)

    # If the non-operator is itself top-level
    elif term_info is None and posn_offset == tuple():
        # TODO I mean, I think this is right?
        struct \
            = subbed

    # Non-operator
    elif term_info is None:
        ref_sub = descend_struct(struct, posn_offset[:-1])

        el_idx = posn_offset[-1]
        ref_sub[el_idx] = subbed

        struct._regenerate_freq(recurse=True)

    return struct


# TODO A little inefficient that we only pick the match object of each match call but ok

def find_subs_identity(test: Operator, identity: Identity, *, depth=1, top_level=False):
    """
    Finds all substitutions for an identity.

    Depth can be set to ``True`` to get all possible substitutions.
    """

    # TODO idea
    # for each identity in an identityset, when applying, keep a list of position offsets for
    # where the identity found a match. then, it can skip matching terms it has tried to match before
    # and that haven't changed.
    # when a sub happens, the branch of the tree (it is basically a tree) is popped and has to be re-matched by all terms
    # the only reason im considering a dict is because once it scans one term somewhere, if the same term comes up elsewhere
    # then it won't have to be matched again.

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
            # print(var_subs, posn_offset, term_info)
            cpy = test.copy()

            # Skip matches that aren't top level
            if top_level and posn_offset != tuple():
                continue

            # Make substitution
            if isinstance(sub_pattern, Callable):
                subbed = sub_pattern(var_subs)
            else:
                subbed = sub_into_pattern(sub_pattern, var_subs)

            # print(subbed)

            cpy = make_sub(cpy, subbed, posn_offset, term_info)
            subs.append(cpy)

            depth -= 1
        except StopIteration:
            return subs

    return subs


def apply_until_constant(op: Operator, i_set: IdentitySet, *, do_eval=True, top_level=False, return_changed=False):
    """Applies identity rules of an identity set until no more can be applied."""

    op_copy = op.copy()

    any_changes = False

    # TODO Make this for Identity() objects too instead of only IdentitySet()s

    while True:
        changed = False
        # prev = op_copy.copy()

        # print('=========== TESTING IDENTITIES ON ', op_copy)

        for i in i_set:
            options = find_subs_identity(op_copy, i, top_level=top_level)

            # print('testing', i.a.pattern, 'on', op)
            # print('matches', options)

            if not options:
                continue

            # print('---------', i.a.pattern)
            # print('    op now:', op_copy)
            # print('    op after:', absorb(options[0]))

            # TODO Not a fan of absorb()ing; the substitution should just replace the original term instead of its insides
            # TODO But i guess not that big a deal since we have a function for it already and it would be better than copying code (sleep on it)
            # TODO Plus we can just eval without an if statement here lol
            # print('applied', i.a.pattern, 'to get', options[0])
            # print('Applied', i.a.pattern, ' for ', op_copy, ' ---> ', absorb(options[0]))
            op_copy = absorb(options[0])

            # todo new
            changed = True
            any_changes = True

        if do_eval:
            # print('EVAL ---------')
            # print('    op now:', op_copy)
            # print('    op after:', evaluate(op_copy))
            op_copy = absorb(evaluate(op_copy))

        # todo why is this here? why not below op_copy = absorb(...)
        # if not eq_struct(op_copy, prev):
        #     any_changes = True
        #     changed = True

        if not changed:
            # print('UNCHANGED', op_copy, prev)
            break

    # TODO This is disgusting
    if not return_changed:
        return op_copy
    else:
        return any_changes, op_copy


def apply_one(op: Operator, i_set: IdentitySet, *, do_eval=True, top_level=False, return_changed=False):
    """Applies at most 1 identity from the given identity set."""

    op_copy = op.copy()
    changed = False

    for i in i_set:
        options = find_subs_identity(op_copy, i, top_level=top_level)

        # print('testing', i.a.pattern, 'on', op)
        # print('matches', options)

        if not options:
            continue

        # print('---------', i.a.pattern)
        # print('    op now:', op_copy)
        # print('    op after:', absorb(options[0]))

        # TODO Not a fan of absorb()ing; the substitution should just replace the original term instead of its insides
        # TODO But i guess not that big a deal since we have a function for it already and it would be better than copying code (sleep on it)
        # TODO Plus we can just eval without an if statement here lol
        # print('applied', i.a.pattern, 'to get', options[0])
        print('Applied', i.a.pattern, ' for ', op_copy, ' ---> ', absorb(options[0]))
        op_copy = absorb(options[0])

        # todo new
        changed = True
        break

    if do_eval:
        # print('EVAL ---------')
        # print('    op now:', op_copy)
        # print('    op after:', evaluate(op_copy))
        op_copy = absorb(evaluate(op_copy))

    if not return_changed:
        return op_copy
    else:
        return changed, op_copy




def apply_greedily(op: Operator, i_set: IdentitySet, metric: Callable, *, depth=10):
    """Applies identities of an identity set according to a certain metric."""

    # TODO No evaluation here

    op_copy = op.copy()
    op_score = metric(op_copy)

    best_branch = None
    best_score = 0

    for i in i_set:
        options = find_subs_identity(op_copy, i)

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
