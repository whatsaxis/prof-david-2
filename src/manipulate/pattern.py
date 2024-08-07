import typing
import itertools
import collections

from src.manipulate.basic import absorb
from src.manipulate.helpers import descend_struct, from_freq
from src.struct.op import Operator, internalize
from src.manipulate.eq import eq_struct
from src.struct.number import Number
from src.struct.unknown import Unknown, Wild

from src.core.assume import Commutative


# TODO Probably extract to Operator


def interrogate(*facts: dict, wilds):
    """Arstotzka-style truth checker."""

    compiled = {}

    for w in wilds:
        fact = None

        for f in facts:
            # TODO HMMMM
            if f.get(w, None) is None:
                continue

            if fact is None:
                fact = f[w]

            if not eq_struct(f[w], fact):
                return False

        compiled[w] = fact

    return compiled


class Pattern:

    def __init__(self, pattern: Operator | Wild | Unknown | Number, wild_conditions=None):
        self.pattern = internalize(pattern)

        self.wild_positions = Pattern.traverse(pattern)
        self.wild_conditions = wild_conditions

    def match(self, test: Operator):
        """Recursively matches a pattern against another object."""

        yield from self._match(test, self.pattern)

    def _match(self, test: Operator, pattern: Operator, *, posn_offset=None, parent=True) -> tuple[dict]:
        """Function to test a pattern against a structure."""

        if posn_offset is None:
            posn_offset = tuple()

        # print('!!!------ matching', test, pattern, parent)

        # TODO This condition may not be right. It has caused issues already [wild against operator].
        if isinstance(pattern, Wild):
            matches = {
                k: (None if k != pattern.symbol else test)
                for k in self.wild_positions.keys()
            }

            # TODO Is it just worth straight up removingitg this eq_struct call? It's double the work since we're already doing a backtracking thing anyway.
            if eq_struct(test, pattern, wild_conditions=self.wild_conditions):
                if parent:
                    # print('testng', test, pattern)
                    yield matches, posn_offset, None
                else:
                    yield {
                        k: (None if k != pattern.symbol else test)
                        for k in self.wild_positions.keys()
                    }

        # TODO Is length condition necessary?
        elif isinstance(pattern, Operator) and type(pattern) == type(test):
            if pattern.ask(Commutative):
                yield from self.match_commutative(test, pattern, posn_offset=posn_offset, parent=parent)
            else:
                yield from self.match_non_commutative(test, pattern, posn_offset=posn_offset, parent=parent)

        # Match nested terms
        if parent is True:
            if not isinstance(test, Operator):
                return

            for i, t in enumerate(test):
                yield from self._match(t, pattern, posn_offset=posn_offset + (i,), parent=True)

    def match_commutative(self, test: Operator, pattern: Operator, *, posn_offset, parent):
        """Test a pattern against a commutative structure."""

        # [Commutative] Sort pattern terms in the order of:

        #   > Constants (numbers / constant unknowns)
        #   > Wilds
        #   > Structures
        #   > Sequence variables

        # To reduce the search space. Because the computation of sequence variables is a nice and pleasant O(n!).
        # NOTE: This may lead to an... odd pattern order.

        pattern = pattern.duplicate(*sorted(pattern.terms, key=Pattern.sort_key))

        def recurse(freq: 'collections.Counter', pat, compiled_fact=None):
            if not compiled_fact:
                compiled_fact = collections.defaultdict(lambda: None)

            if len(pat) == 0:
                if parent:
                    yield dict(compiled_fact), posn_offset, freq
                else:
                    yield dict(compiled_fact)

                # print('    ! yielded', test, dict(compiled_fact))

                return

            # if parent:
            #     print('--------', test, '  |  ', pat[0], ' ', dict(compiled_fact))
            #     print(dict(freq))

            pat_term = pat[0]

            # [Optimization 1] If the current pattern term is a wild, and its value is already known, simply consult the frequency table.
            if isinstance(pat_term, Wild) and compiled_fact[pat_term] is not None:

                ft_copy = freq.copy()

                # Absorb terms of the compiled fact for sequence variables within the same structure
                #   e.g. matching pattern 《u》 - 《u》 to Add[Multiply[3, x], Multiply[-1, 3, x]]
                #   results in 《u》 = Multiply[3, x], but we can't directly match that into Multiply[-1, 3, x] w/o absorbing
                if pat_term.sequence and isinstance(compiled_fact[pat_term], Operator) and type(compiled_fact[pat_term]) == type(test):
                    for sub_term in compiled_fact[pat_term]:
                        if freq[sub_term] == 0:
                            return

                        ft_copy[sub_term] -= 1

                # Otherwise treat them and other wilds as normal wilds
                else:
                    if freq[compiled_fact[pat_term]] == 0:
                        return

                    ft_copy[compiled_fact[pat_term]] -= 1

                # The compiled table will not change after this step
                yield from recurse(ft_copy, pat[1:], compiled_fact)

            # TODO For non-parent matching, sequence variables MUST somehow cover all the terms of the structure.

            # if parent: print(dict(freq), pat_term)

            sequence, possible_terms_seq, ranges_seq = False, [], []
            if isinstance(pat_term, Wild) and pat_term.sequence:
                sequence = True

            for t in freq:
                # Test if there are any remaining terms of that type
                if freq[t] == 0:
                    continue

                # Test if term matches pattern term
                if not eq_struct(t, pat_term, self.wild_conditions):
                    # if parent: print('    -> exited here because', t, pat_term, 'not equal')
                    continue

                # Check which terms can match with the sequence variable
                if sequence:

                    if eq_struct(t, pat_term, wild_conditions=self.wild_conditions):
                        possible_terms_seq.append(t)
                        ranges_seq.append(range(0, freq[t] + 1))

                    continue

                # Test if there is a contradiction within this branch
                # posn_offset isn't passed as it is not used.
                term_facts = [
                    p
                    for p in self._match(
                        t,
                        pat_term,

                        parent=False
                    )
                ]

                # if parent:
                #     print('  -- exploring branch', t, 'for', pat[0])
                #     print('term facts for', t, pat[0], term_facts)

                # If the term has wilds but none were recorded, that means there is a contradiction. Hence, the whole match is invalid.
                # If wilds were recorded, contradictions will be detected in the interrogate() call below.
                if (isinstance(pat_term, Operator) and pat_term.has_wilds and not term_facts) or (isinstance(pat_term, Wild) and not term_facts):
                    # print('[1]', pat[0], t)
                    continue

                # Or, there is a constant term to be matched
                elif (isinstance(pat_term, Operator) and not pat_term.has_wilds) or (not isinstance(pat_term, Wild) and not isinstance(pat_term, Operator)):
                    # print('[2]', pat[0], t)
                    ft_copy = freq.copy()
                    ft_copy[t] -= 1

                    yield from recurse(ft_copy, pat[1:], compiled_fact)

                # Otherwise, match normally.
                # Since there can be multiple valid matches, a new branch is created for each of them
                else:

                    # print('[3]', pat[0], t)

                    for tf in term_facts:
                        # print('interpretation', tf, compiled_fact)
                        compiled = interrogate(compiled_fact, tf, wilds=self.wild_positions.keys())

                        if compiled is False:
                            # print('variables do not agree', dict(compiled_fact), dict(tf))
                            continue

                        ft_copy = freq.copy()
                        ft_copy[t] -= 1
                        # print('  > yielded for', t, pat[0], tf, dict(compiled))
                        yield from recurse(ft_copy, pat[1:], compiled)

                # print('    term facts for', test, ':', term_facts, dict(compiled_fact))

            if sequence:
                # [Optimization 2] If there is only 1 sequence variable (which usually is... why would you need more), just return the rest of the terms.

                # print('k', dict(compiled_fact), test, pattern, pattern.num_sequence)

                if pattern.num_sequence == 1:
                    # Oops! Not all terms can match; exit
                    if len(possible_terms_seq) != sum(1 if c != 0 else 0 for c in freq.values()):
                        return

                    # print('aasdsad', compiled_fact, {pat_term.symbol: absorb(pattern.duplicate(*from_freq(freq)))})
                    # print('asdasd', interrogate(compiled_fact, {pat_term: absorb(pattern.duplicate(*from_freq(freq)))}, wilds=self.wild_positions.keys()))
                    seq_yield = interrogate(compiled_fact, {pat_term: absorb(pattern.duplicate(*from_freq(freq)))}, wilds=self.wild_positions.keys())

                    if parent:
                        yield seq_yield, posn_offset
                    else:
                        yield seq_yield

                else:

                    # TODO

                    # Π (freq[i] + 1) combinations. All hail the gamma function.

                    for possible_freq in itertools.product(*ranges_seq):
                        o = {}

                        for i, t in enumerate(possible_terms_seq):
                            o[t] = possible_freq[i]

                        yield interrogate(compiled_fact, {pat_term: absorb(pattern.duplicate(*from_freq(o)))}, wilds=self.wild_positions.keys())

        yield from recurse(test.freq_table, pattern.terms)

    def match_non_commutative(self, test: Operator, pattern: Operator, *, posn_offset, parent):
        """Tests a pattern against a non-commutative structure."""

        # TODO Sequence

        for i in range(
            len(test) - len(pattern) + 1
        ):
            ok = True
            stm_all = []

            for j, pat_term in enumerate(pattern):

                # If a term does not match, exit
                if not eq_struct(pat_term, test[i + j], self.wild_conditions):
                    ok = False
                    break

                # Recursively call match() on sub-terms for the same pattern, since commutativity may vary
                # posn_offset isn't passed as it is not used.
                sub_term_matches = [
                    p

                    for p in self._match(
                        test[i + j],
                        pat_term,

                        parent=False
                    )
                ]

                # If the term has wilds but none were recorded, that means there is a contradiction. Hence, the whole match is invalid.
                # If wilds were recorded, contradictions will be detected in the interrogate() call below.
                if (isinstance(pat_term, Operator) and pat_term.has_wilds and not sub_term_matches) or (isinstance(pat_term, Wild) and not sub_term_matches):
                    continue

                if sub_term_matches:
                    stm_all.append(sub_term_matches)

            if not ok:
                continue

            # There may be multiple possible matches from sub-terms; nothing a Cartesian product can't handle
            for possible in itertools.product(*stm_all):
                it = interrogate(*possible, wilds=self.wild_positions.keys())

                if not ok or not it:
                    continue

                if parent:
                    yield dict(it), posn_offset, (i, i + len(pattern))
                else:
                    yield dict(it)

                # print('!! yielded', test, pattern, dict(it))

    @staticmethod
    def traverse(struct: Operator, position: tuple[int] | None = None):
        """Recursively traverse a structure, noting the position of all wildcards."""

        if not isinstance(struct, Operator):
            if isinstance(struct, Wild):
                return {struct.symbol: [0]}
            return {}

        # TODO Clean

        if position is None:
            position = tuple()

        wildcards = {}

        for idx, t in enumerate(struct):
            pc = position + (idx,)

            # Record wildcard position
            if isinstance(t, Wild):
                sym = t.symbol

                if sym in wildcards:
                    wildcards[sym].append(pc)
                else:
                    wildcards[sym] = [pc]

            # Recursive traversal and merging of wildcard positions
            elif isinstance(t, Operator):
                wc = Pattern.traverse(t, pc)

                for k, v in wc.items():
                    if k not in wildcards:
                        wildcards[k] = []

                    wildcards[k] += v

        return {k: tuple(v) for k, v in wildcards.items()}

    @staticmethod
    def sort_key(term):
        if isinstance(term, Wild):
            if term.sequence is True:
                return 5

            return 2

        if isinstance(term, Number | Unknown):
            return 1

        if isinstance(term, Operator):
            return 3
