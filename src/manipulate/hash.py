# import string
#
# from src.core.assume import Commutative
#
# from src.struct.op import Operator
# from src.struct.unknown import Unknown, Wild
# from src.struct.number import Number
#
#
# # so long as pairwise sorting order is maintained
#
# # the issue with sorting using hashes is that with wilds, the order of the unknowns is not necessarily preserved
# # in order to maintain only the STRUCTURE, all constants, unknowns, etc. have to be set to a constant. probably 0.
#
# # A possible hash idea is to find all wilds and unknowns in a structure and map them to the naturals.
# # Then we just hash normally. This results in symbol-independence. Or set up a context manager hash?
# # WHAT ABOUT THE CONSTANTS? probably just wise to ignore them, since they can be collected and stuff
#
# # After this the following algo can be used for commutative structures for lazily generating matches:
#
# # - for the first term, find the first one which matches by iterating through the array
# # - if no matches, exit
# # - recursively call on the slice after the index of the first match (pairwise ordering means that all second terms will be after the first match of the first term)
# # - linear (kind of) soln?
#
#
# # TODO Experiment with this for fast equality checking
#
# class HashContext:
#     """Context manager for symbol-independent hash generation."""
#
#     def __init__(self):
#         self.symbol_map = {}
#
#     def i_hash(self, obj: Operator | Unknown | Wild | Number):
#         """Hashing function."""
#
#         if isinstance(obj, Unknown | Wild):
#             if obj.symbol in self.symbol_map:
#                 return self.symbol_map[obj.symbol]
#
#             # Symbol independence is achieved by taking the hash of a string corresponding to the index of the symbol.
#             # This is an intermediary step done to minimise hash collisions.
#
#             self.symbol_map[obj.symbol] = hash(
#                 'z' * (len(self.symbol_map) // 26) +
#                 string.ascii_lowercase[len(self.symbol_map) % 26]
#             )
#
#         # if isinstance(obj, Number):
#         #     return 0
#
#         if obj.ask(Commutative):
#
#             # Commutative hash function
#             return sum(self.i_hash(t) for t in obj)
#
#         return hash(tuple(self.i_hash(t) for t in obj))
#
#     def __enter__(self):
#         return self.i_hash
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         pass
#
#
# # todo out of the way because this is ugly
# # class PatternOld:
# #     """Pattern object, responsible for checking patterns, to be used in substitution and manipulations."""
# #
# #     def __init__(self, p: Operator):
# #         self.__pattern = p
# #         self.__wild_positions = PatternOld.traverse(self.pattern)
# #
# #     def __str__(self):
# #         return f'⌗[{ repr(self.pattern) }]'
# #
# #     def __repr__(self):
# #         return str(self)
# #
# #     @property
# #     def pattern(self):
# #         return self.__pattern
# #
# #     """
# #     Manipulations
# #     """
# #
# #     def match(self, test: Operator) -> tuple[dict]:
# #         """Function to match a pattern against a structure."""
# #
# #         return tuple(
# #             p
# #
# #             for p in PatternOld._match(test, self.pattern, positions=self.__wild_positions)
# #
# #             # Check for empty / non-valid solutions
# #             if all(v for v in p[0].values())
# #         )
# #
# #     @classmethod
# #     def _match(cls, test: Operator, pattern: Operator, *, positions) -> tuple[dict]:
# #         """Function to test a pattern against a structure."""
# #
# #         if not isinstance(test, Operator):
# #             return eq_struct(pattern, test)
# #
# #         if type(pattern) == type(test):
# #             if pattern.ask(Commutative):
# #                 yield from cls._match_commutative(test, pattern, positions=positions)
# #             else:
# #                 yield from cls._match_non_commutative(test, pattern, positions=positions)
# #
# #         # Match nested terms
# #         for t in test:
# #             yield from cls._match(t, pattern, positions=positions)
# #
# #     @classmethod
# #     def _match_non_commutative(cls, test: Operator, pattern: Operator, *, positions):
# #         """Function to test a pattern against a non-commutative structure."""
# #
# #         for i in range(
# #             len(test) - len(pattern) + 1
# #         ):
# #             ok = True
# #             sl = test.duplicate(
# #                 *test[i:i + len(pattern)]
# #             )
# #
# #             compiled = []
# #
# #             # Comparison stage
# #             for j, t in enumerate(pattern):
# #
# #                 if not eq_struct(t, sl[i + j]):
# #                     ok = False
# #                     break
# #
# #                 # Extract from sub-terms
# #                 sub_term_yields = [
# #                     p[0] if isinstance(p, tuple) else p
# #                     for p in PatternOld._match(
# #                         sl[i + j],
# #                         t,
# #                         positions={
# #                             wild: [pos[1:] for pos in pos_list if pos[0] == j]
# #                             for wild, pos_list in positions.items()
# #                         }
# #                     )
# #                 ]
# #
# #                 if sub_term_yields:
# #                     compiled.append(sub_term_yields)
# #
# #             if not ok:
# #                 continue
# #
# #             # Extract and yield values
# #             ex = cls._extract(sl, pattern, positions, layer=True)
# #
# #             if not ex:
# #                 continue
# #
# #             # Run through permutations of possible matches in sub-terms
# #             for find in itertools.product([ex], *compiled):
# #                 test = interrogate(*find)
# #
# #                 if test:
# #                     yield test, i
# #
# #     @classmethod
# #     def _match_commutative(cls, test: Operator, pattern: Operator, *, depth=100, depth_hard=100_000, positions):
# #         """Function to test a pattern against a commutative structure."""
# #
# #         # Filter out duplicate static terms
# #         # TODO Combine this with below loop. Somehow. I hate this solution. Please change it. NOW.
# #
# #         # TODO What garbage is this
# #         # mt, mp = [True for _ in range(len(test))], [True for _ in range(len(pattern))]
# #         #
# #         # for i, ta in enumerate(test):
# #         #     if not mt[i]:
# #         #         continue
# #         #
# #         #     for j, tb in enumerate(pattern):
# #         #
# #         #         # Can't remove wilds!
# #         #         if isinstance(tb, Wild) or (isinstance(tb, Operator) and tb.has_wilds) or not mp[j]:
# #         #             continue
# #         #
# #         #         if eq_struct(ta, tb):
# #         #             mt[i] = False
# #         #             mp[j] = False
# #         #
# #         #             break
# #         #
# #         # test = test.duplicate(*(t for i, t in enumerate(test) if mt[i]))
# #         # pattern = pattern.duplicate(*(t for i, t in enumerate(pattern) if mp[i]))
# #
# #         # Find possibilities for each wild
# #
# #         m = {}
# #
# #         for i, ta in enumerate(test):
# #             for j, tb in enumerate(pattern):
# #
# #                 # Equality checking
# #                 if eq_struct(ta, tb):
# #
# #                     if m.get(j, False):
# #                         m[j].add(i)
# #                         continue
# #
# #                     m[j] = {i}
# #
# #         # Yield (valid) iterator values values until depth is reached
# #
# #         p = product_no_replace(
# #             *[
# #                 t[1]
# #
# #                 # dict.values() returns values in insertion order, NOT sorted order of keys.
# #                 # We must sort in order to get a configuration aligning with the pattern, for a linear comparison.
# #                 for t in sorted(m.items())
# #             ]
# #         )
# #
# #         while depth > 0 and depth_hard > 0:
# #
# #             depth_hard -= 1
# #
# #             try:
# #                 nx = next(p)
# #
# #                 compiled = []
# #
# #                 dp = test.duplicate(
# #                     *tuple(
# #                         test[t]
# #                         for t in nx
# #                     )
# #                 )
# #
# #                 # Quick exit if a possible combination does
# #                 # not actually satisfy structure; bad input
# #                 # TODO Is this necessary?
# #                 if not eq_struct(dp, pattern):
# #                     return False
# #
# #                 # Extract wilds from sub terms
# #
# #                 for i, pt in enumerate(pattern):
# #
# #                     # Extract from sub-terms
# #                     sub_term_yields = [
# #                         p[0] if isinstance(p, tuple) else p
# #                         for p in PatternOld._match(
# #                             dp[i],
# #                             pt,
# #                             positions={
# #                                 wild: [pos[1:] for pos in pos_list if pos[0] == i]
# #                                 for wild, pos_list in positions.items()
# #                             }
# #                         )
# #                     ]
# #
# #                     if sub_term_yields:
# #                         compiled.append(sub_term_yields)
# #
# #                 # Descend wild positions in pattern in order to
# #                 # extract & confirm valid matches
# #
# #                 wilds = cls._extract(dp, pattern, positions, layer=True)
# #
# #                 if not wilds:
# #                     continue
# #
# #                 # Run through permutations of possible matches in sub-terms
# #                 for find in itertools.product([wilds], *compiled):
# #                     cmp = interrogate(*find)
# #
# #                     if cmp is False:
# #                         continue
# #
# #                     # Yay, a match!
# #                     depth -= 1
# #
# #                     yield cmp, nx
# #
# #             except StopIteration:
# #                 return
# #
# #     @staticmethod
# #     def _extract(term: Operator, pattern: Operator, positions, *, layer=False):
# #         """General extraction function of values in structures."""
# #
# #         # Not same structure
# #         if not eq_struct(pattern, term):
# #             return False
# #
# #         wilds_out = {}
# #
# #         for wild in positions:
# #             obj = None
# #
# #             for pos in positions[wild]:
# #
# #                 # [Layer setting]
# #                 #   Not top layer wild; to be handled by a recursive
# #                 #   call in a higher function on based on commutativity
# #                 if layer and len(pos) > 1:
# #                     continue
# #
# #                 # Descend structure from position tuple
# #                 o = descend_struct(
# #                     term,
# #                     pos
# #                 )
# #
# #                 # Check equality
# #                 if not obj:
# #                     obj = o
# #                 else:
# #                     if not eq_struct(o, obj):
# #                         return False
# #
# #             # Yay!
# #             wilds_out[wild] = obj
# #
# #         return wilds_out
# #
# #     def substitute(self, values: dict):
# #         """Substitution function into the pattern."""
# #
# #         pattern = self.pattern
# #
# #         for wc, pos_list in self.__wild_positions.items():
# #
# #             for pos in pos_list:
# #
# #                 # TODO Find a better way. Seriously.
# #                 exec(
# #                     'pattern' +
# #                     ''.join(
# #                         f'[{ n }]'
# #                         for n in pos
# #                     ) +
# #                     ' = values[wc]'
# #                 )
# #
# #         return pattern
# #
# #     """
# #     Operator traversal
# #     """
# #
# #     @staticmethod
# #     def traverse(struct: Operator, position: list[int] | None = None):
# #         """Recursively traverse a structure, noting the position of all wildcards."""
# #
# #         if position is None:
# #             position = []
# #
# #         wildcards = {}
# #
# #         for idx, t in enumerate(struct):
# #             pc = position + [idx]
# #
# #             # Record wildcard position
# #             if isinstance(t, Wild):
# #                 sym = t.symbol
# #
# #                 if sym in wildcards:
# #                     wildcards[sym].append(pc)
# #                 else:
# #                     wildcards[sym] = [pc]
# #
# #             # Recursive traversal and merging of wildcard positions
# #             elif isinstance(t, Operator):
# #                 wc = PatternOld.traverse(t, pc)
# #
# #                 for k, v in wc.items():
# #                     if k not in wildcards:
# #                         wildcards[k] = []
# #
# #                     wildcards[k] += v
# #
# #         return wildcards
#
# ####
#
# cnt = collections.defaultdict(lambda: 0)
# indices = collections.defaultdict(lambda: [])
#
# for i, t in enumerate(test):
#     cnt[t] += 1
#     indices[t].append(posn_offset + (i,))
#
# # Find all possible options for each pattern term
#
# options = {}
#
# for i, distinct_term in enumerate(cnt):
#     for j, pattern_term in enumerate(pattern):
#
#         # Equality checking
#         if eq_struct(distinct_term, pattern_term):
#
#             # In theory, if cnt[t] exceeds
#
#             if j in options:
#                 options[j].add(distinct_term)
#                 continue
#
#             options[j] = {distinct_term}
#         else:
#
#             if j not in options:
#                 # Not using a defaultdict() here, so we can see if there are any pattern terms
#                 # which do not match with any of the terms of the test structure
#                 options[j] = set()
#
# ####
#
# def product_no_replace(groups: tuple[set, ...], frequencies: dict):
#     """Product function without replacement. Accounts for the frequencies of each term."""
#
#     # todo some sort of local memo
#
#     # No matches for specific term - exit!
#     if not groups or not groups[0]:
#         yield ()
#         return
#
#     for g in groups[0]:
#
#         # todo what tf is this for
#         # if g == set() or g == tuple():
#         #     yield ()
#         #     continue
#
#         frc = frequencies.copy()
#         frc[g] -= 1
#
#         gc = copy.deepcopy(groups)[1:]
#
#         # Remove dupes (if they ran out)
#         if frc[g] == 0:
#             for idx in range(len(gc)):
#                 gc[idx].discard(g)
#
#         # Yield solution
#         for sol in product_no_replace(gc, frequencies=frc):
#             yield [
#                 g, *sol
#             ]
#
#
# ####
#
# import copy
# import itertools
# import collections
#
# from src.manipulate.helpers import descend_struct
# from src.struct.op import Operator, internalize
# from src.manipulate.eq import eq_struct, eq_type
# from src.struct.unknown import Wild
#
# from src.core.assume import Commutative
#
#
# # TODO Probably extract to Operator
#
#
# def interrogate(*facts: dict):
#     """Arstotzka-style truth checker."""
#
#     compiled = {}
#
#     # facts[0] always contains all the wilds, since it is always from the extracted top-level wilds, whose
#     # keys are derived from the wild positions of the Pattern() object
#     wilds = facts[0].keys()
#
#     for w in wilds:
#         fact = None
#
#         for f in facts:
#             if not fact:
#                 fact = f[w]
#                 continue
#
#             if f[w] is None:
#                 continue
#
#             if not eq_struct(f[w], fact):
#                 return False
#
#         compiled[w] = fact
#
#     return compiled
#
#
# def product_no_replace(groups: tuple[list, ...], frequencies: dict):
#     """Product function without replacement. Accounts for the frequencies of each term."""
#
#     # todo some sort of local memo
#
#     # No matches for specific term - exit!
#     if not groups or not groups[0]:
#         yield ()
#         return
#
#     for g in groups[0]:
#
#         if frequencies[g] == 0:
#             continue
#
#         frc = frequencies.copy()
#         frc[g] -= 1
#
#         gc = copy.deepcopy(groups)[1:]
#
#         # Yield solution
#         for sol in product_no_replace(gc, frequencies=frc):
#             yield [
#                 g, *sol
#             ]
#
#
# class Pattern:
#
#     def __init__(self, pattern: Operator, wild_conditions=None):
#         self.pattern = internalize(pattern)
#
#         self.wild_positions = Pattern.traverse(pattern)
#         self.wild_conditions = wild_conditions
#
#     def match(self, test: Operator):
#         """Recursively matches a pattern against another object."""
#
#         yield from self._match(test, self.pattern, positions=self.wild_positions)
#
#     def _match(self, test: Operator, pattern: Operator, *, positions, posn_offset=None, parent=True) -> tuple[dict]:
#         """Function to test a pattern against a structure."""
#
#         if posn_offset is None:
#             posn_offset = tuple()
#
#         # TODO This condition may not be right. It has caused issues already [wild against operator].
#         if isinstance(pattern, Wild):
#             yield {
#                 k: (None if k != pattern.symbol else test)
#                 for k in positions.keys()
#             }
#             return
#
#         if not isinstance(test, Operator):
#             return
#
#         # TODO Is length condition necessary?
#         if eq_type(test, pattern) and len(test) >= len(pattern):
#             if pattern.ask(Commutative):
#                 yield from self.match_commutative(test, pattern, positions=positions, posn_offset=posn_offset,
#                                                   parent=parent)
#             else:
#                 yield from self.match_non_commutative(test, pattern, positions=positions, posn_offset=posn_offset,
#                                                       parent=parent)
#
#         # Match nested terms
#         if parent is True:
#             for i, t in enumerate(test):
#                 yield from self._match(t, pattern, positions=positions, posn_offset=posn_offset + (i,), parent=True)
#
#     def match_commutative(self, test: Operator, pattern: Operator, positions, *, posn_offset, parent):
#         """Test a pattern against a commutative structure."""
#
#         """
#         find all distinct elements with a frequency table
#
#         find all options using the code from the old thing
#
#         find the unknowns that are contained within each term (is this worth it lol)
#         """
#         # TODO ^^^ Possible improvement is to just skip over those which dont contain a certain unknown given
#         # TODO that a pattern term does but i dunno
#         # TODO Refactor everything using self instead of @classmethod
#
#         # TODO Some sort of context manager cache so we don't have to eq_exact each term with each other term in every pattern every time (should save LOTS of time)
#
#         """
#         it appears that this depends on eq_struct() being correct, as otherwise sub_term_matches ends up being
#         empty for some terms and it just yields a solution, which makes sense
#         """
#
#         # Find all distinct elements in the structure
#
#         cnt = collections.defaultdict(lambda: 0)
#         indices = collections.defaultdict(lambda: [])
#
#         # Find all possible options for each pattern term
#
#         options = {}
#
#         for i, term in enumerate(test):
#
#             # In theory, if cnt[t] exceeds 1, it has already been compared to every
#             # pattern term, meaning we already KNOW it is in the options{} dictionary.
#             # Hence, we do not need to use sets, and order is maintained.
#
#             if cnt[term] == 0:
#                 for j, pattern_term in enumerate(pattern):
#
#                     # Equality checking
#                     if eq_struct(term, pattern_term, wild_conditions=self.wild_conditions):
#                         if j in options:
#                             options[j].append(term)
#                             continue
#
#                         options[j] = [term]
#                     else:
#
#                         if j not in options:
#                             # Not using a defaultdict() here, so we can see if there are any pattern terms
#                             # which do not match with any of the terms of the test structure
#                             options[j] = []
#
#             cnt[term] += 1
#             indices[term].append(posn_offset + (i,))
#
#         # TODO For some reason eq_struct() is wrong and also pattern matcher is not checking the variables?
#
#         # One or more pattern terms match to no terms from structure; exit
#         if any(not v for v in options.values()):
#             return
#
#         # Generate solutions
#
#         p = product_no_replace(
#             tuple(
#                 t[1]
#
#                 # dict.values() returns values in insertion order, NOT sorted order of keys.
#                 # We must sort in order to get a configuration aligning with the pattern, for a linear comparison.
#                 for t in sorted(options.items())
#             ),
#             frequencies=cnt
#         )
#
#         while True:
#
#             try:
#                 # Generate a possible match
#                 nx = next(p)
#                 stm_all = []
#                 # Some pattern terms do not match with any terms from test structure, so exit
#                 if not nx:
#                     return
#
#                 # if parent: print('----', nx)
#
#                 # Extract values and check if they match the pattern
#                 for i, pat_term in enumerate(pattern):
#
#                     # Recursively call match() on sub-terms for the same pattern, since commutativity may vary
#                     # TODO Combine this into a function somewhere
#                     # print('    ', nx[i], pat_term)
#                     sub_term_matches = [
#                         p
#
#                         for p in self._match(
#                             nx[i],
#                             pat_term,
#
#                             # Shift positions of wilds for this term
#                             positions={
#                                 wild: [pos[1:] for pos in pos_list if pos[0] == i]
#                                 for wild, pos_list in positions.items()
#                             },
#                             parent=False
#                         )
#                     ]
#
#                     if sub_term_matches:
#                         stm_all.append(sub_term_matches)
#                 # if parent: print(stm_all)
#                 for sol in Pattern.gen_solutions(test.duplicate(*nx), pattern, positions, stm_all):
#                     if parent:
#                         yield sol, tuple(set(indices[t]) for t in nx)
#                     else:
#                         yield sol
#
#             except StopIteration:
#                 return
#
#     def match_non_commutative(self, test: Operator, pattern: Operator, positions, *, posn_offset, parent):
#         """Tests a pattern against a non-commutative structure."""
#
#         for i in range(
#                 len(test) - len(pattern) + 1
#         ):
#             ok = True
#             stm_all = []
#
#             for j, pat_term in enumerate(pattern):
#
#                 # If a term does not match, exit
#                 if not eq_struct(pat_term, test[i + j], wild_conditions=self.wild_conditions):
#                     ok = False
#                     break
#
#                 # Recursively call match() on sub-terms for the same pattern, since commutativity may vary
#                 sub_term_matches = [
#                     p
#
#                     for p in self._match(
#                         test[i + j],
#                         pat_term,
#
#                         # Shift positions of wilds for this term
#                         positions={
#                             wild: [pos[1:] for pos in pos_list if pos[0] == j]
#                             for wild, pos_list in positions.items()
#                         },
#                         parent=False
#                     )
#                 ]
#
#                 if sub_term_matches:
#                     stm_all.append(sub_term_matches)
#
#             if not ok:
#                 continue
#
#             # Generating solutions
#
#             canon = test.duplicate(*test[i:i + len(pattern)])
#
#             for sol in Pattern.gen_solutions(canon, pattern, positions, stm_all):
#                 if parent:
#                     yield sol, tuple({posn_offset + (idx,), } for idx in range(i, i + len(pattern)))
#                 else:
#                     yield sol
#
#     @staticmethod
#     def gen_solutions(term: Operator, pattern: Operator, positions, stm_all):
#         """Checks facts and generates solutions from sub-term matches and top-level matches."""
#
#         """Top-level matches"""
#
#         # Not same structure
#         # if not eq_struct(pattern, term):
#         #     print('L')
#         #     return False
#
#         # TODO Do we actually need this? Doesn't sub term matches do it for us?
#         # wilds_top = {}
#         #
#         # for wild in positions:
#         #     obj = None
#         #
#         #     for pos in positions[wild]:
#         #
#         #         # [Layering]
#         #         #   Not top layer wild; handled by a recursive call
#         #         #   in a higher function on based on commutativity
#         #         if len(pos) > 1:
#         #             continue
#         #
#         #         # Descend structure from position tuple
#         #         o = descend_struct(
#         #             term,
#         #             pos
#         #         )
#         #
#         #         # Check equality
#         #         if not obj:
#         #             obj = o
#         #         else:
#         #             if not eq_struct(o, obj):
#         #                 return False
#         #
#         #     # Yay!
#         #     wilds_top[wild] = obj
#
#         """Comparing to sub-term matches"""
#
#         # TODO for maybe in itertools.product([wilds_top], *stm_all):
#         for maybe in itertools.product(*stm_all):
#             compiled = interrogate(*maybe)
#             # print(compiled)
#             if compiled:
#                 yield compiled
#
#     @staticmethod
#     def traverse(struct: Operator, position: tuple[int] | None = None):
#         """Recursively traverse a structure, noting the position of all wildcards."""
#
#         if not isinstance(struct, Operator):
#             if isinstance(struct, Wild):
#                 return {struct.symbol: [0]}
#             return {}
#
#         # TODO Clean
#
#         if position is None:
#             position = tuple()
#
#         wildcards = {}
#
#         for idx, t in enumerate(struct):
#             pc = position + (idx,)
#
#             # Record wildcard position
#             if isinstance(t, Wild):
#                 sym = t.symbol
#
#                 if sym in wildcards:
#                     wildcards[sym].append(pc)
#                 else:
#                     wildcards[sym] = [pc]
#
#             # Recursive traversal and merging of wildcard positions
#             elif isinstance(t, Operator):
#                 wc = Pattern.traverse(t, pc)
#
#                 for k, v in wc.items():
#                     if k not in wildcards:
#                         wildcards[k] = []
#
#                     wildcards[k] += v
#
#         return {k: tuple(v) for k, v in wildcards.items()}
