from collections import defaultdict

from typing import Callable

from src.core.io import AssumptionIO
from src.core.error import InvalidImplication, Contradiction


class Assumption(AssumptionIO):
    """
    | An assumption.
    """

    def __init__(self, name: str):
        super().__init__(name)


class AssumptionSet:
    """
    | A set of assumptions, along with predicates connecting them.
    |
    | Unknown assumptions are semantically represented by `None`.
    """

    def __init__(self, *predicates, **facts):
        self.assumptions: defaultdict[str, bool | None] = defaultdict(lambda: None, facts)
        self.predicates = predicates

        # self.update()

    def ask(self, expr: Assumption | AssumptionIO | str | tuple):
        """Evaluate the truthiness of an assumption expression."""

        if isinstance(expr, str):
            return self.assumptions[expr]

        return self.assumptions[expr.payload]

        # op, *terms = expr.payload \
        #     if isinstance(expr, AssumptionIO) \
        #     else expr
        #
        # asked = tuple(
        #     self.ask(t) if self.ask(t) is not None else False
        #     for t in terms
        # )
        #
        # return AssumptionIO.operators[op](*asked)

    def set(self, asm: Assumption | str, value: bool | None):
        """Set the value of an assumption."""

        self.assumptions[asm] = value
        # self.update()

    def _set_simple(self, expr: str | tuple, value: bool):
        """Sets the value of expressions in implications."""

        # NOT
        if isinstance(expr, tuple):
            asm_before = self.assumptions[expr[1]]
            self.assumptions[expr[1]] = asm_after = not value
        else:
            asm_before = self.assumptions[expr]
            self.assumptions[expr] = asm_after = value

        # Detect changes
        return asm_before != asm_after

    def update(self):
        """Update the assumptions based on the defined predicates."""

        # TODO Holy this is slow

        # Loop to follow chains of implications, to make the order of definition irrelevant.
        # Will never go into an infinite cycle as a contradiction would occur.

        while True:
            changed = False

            for p in self.predicates:

                # Invalid implication checks
                if not isinstance(p, tuple):
                    raise InvalidImplication(f'Attempting to use a standalone statement as a predicate! [{ p }]')

                rel, left, right = p

                if rel not in {'equiv', 'implies'}:
                    raise InvalidImplication(f'Attempting to use a standalone statement as a predicate! [{ p }]')

                # Check for compound implications
                if not isinstance(right, str) and (right[0] != 'not' or not isinstance(right[1], str)):
                    raise InvalidImplication(f'Cannot imply a compound statement! [{ right }]')

                # Unknown; skip predicate
                if self.ask(left) is None:
                    continue

                if rel == 'implies':
                    # True implies False
                    if self.ask(left) is True:

                        if self.ask(right) is False:
                            raise Contradiction(f'{ left } is True, but implies an already False statement ({ right }).')

                        changed = self._set_simple(right, True)

                elif rel == 'equiv':
                    if self.ask(left) != self.ask(right) and self.ask(right) is not None:
                        raise Contradiction(
                            f'Equivalence not satisfied! ({ left } = { self.ask(left) }) ≢ ({ right } = { self.ask(right) })')

                    changed = self._set_simple(right, self.ask(left))

            if not changed:
                break

    def create(self, **facts):
        """Initialize a copy of an assumption set with some facts."""

        return AssumptionSet(*self.predicates, **(self.assumptions | facts))

    def __eq__(self, other: 'AssumptionSet'):
        return self.assumptions == other.assumptions

    def __str__(self):
        formatted = []
        for k, v in self.assumptions.items():
            formatted.append(f'{ k }={ v }')

        return f'AssumptionSet[{ ", ".join(formatted) }]'


def assume(*asms: Assumption | AssumptionIO | str | tuple, recursive=False):
    """Helper decorator for methods to validate required assumptions."""

    # TODO Recursive option

    def func_wrapper(func: Callable):
        def wrapper(obj):
            for a in asms:

                # Assumption not satisfied → No manipulations
                if not obj.ask(a):
                    return obj

            return func(obj)

        return wrapper
    return func_wrapper


Commutative, Associative, Unary = map(Assumption, ('commutative', 'associative', 'unary'))
Reflexive, Symmetric, Transitive = map(Assumption, ('reflexive', 'symmetric', 'transitive'))
Integer, Rational, Irrational, Positive, Negative, NonPositive, NonNegative, Prime, Composite = map(Assumption,
                                                                                                    ('integer', 'rational', 'irrational',
                                                                                                     'positive', 'negative', 'non_positive', 'non_negative',
                                                                                                     'prime', 'composite'))

EmptyAssumptions = AssumptionSet()

NumberAssumptions = AssumptionSet(
    # Sets TODO comment?
    ~Irrational <= Rational,
    Irrational > ~Integer,

    # Positive and negative
    ~Negative <= Positive,

    Negative > NonPositive,
    Positive > NonNegative,

    # Primality
    Prime & Integer > ~Composite,
    Composite & Integer > ~Prime,

    ~Integer > ~Prime,
    ~Integer > ~Composite,
)

OperatorAssumptions = AssumptionSet(commutative=None, associative=None, unary=None)  # TODO unary implies associative

RelationAssumptions = AssumptionSet(reflexive=None, symmetric=None, transitive=None, linear=None)
