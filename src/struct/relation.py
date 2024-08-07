from src.core.base import DavidBase
from src.core.assume import RelationAssumptions, Symmetric
from src.struct.op import Log, internalize

from src.struct.unknown import Wild

from src.manipulate.basic import absorb
from src.manipulate.pattern import Pattern
from src.manipulate.substitute import substitute


class Relation(DavidBase):
    """Number base class."""

    # 'w' is the relation wild, for manipulations with relations.
    REL_WILD_SYMBOL = 'w'
    w = Wild(REL_WILD_SYMBOL)

    def __init__(self, left: DavidBase, symbol: str, right: DavidBase, **facts):
        super().__init__(RelationAssumptions.create(**facts))

        self.symbol = symbol

        # TODO Wow we really need an internalize decorator
        self.left = internalize(left)
        self.right = internalize(right)

    def __hash__(self):
        if self.ask(Symmetric):
            return hash(self.left) + hash(self.right)

        return hash((self.left, self.right))

    def __str__(self):
        return f'{ str(self.left) } { self.symbol } { str(self.right) }'

    # TODO Manipulation functions

    def apply(self, p: Pattern):
        """Applies to both sides of a relation."""

        self.left = absorb(substitute(p, {Relation.REL_WILD_SYMBOL: self.left}))
        self.right = absorb(substitute(p, {Relation.REL_WILD_SYMBOL: self.right}))

        return self

    def add(self, term):
        raise NotImplementedError()

    def mul(self, term):
        raise NotImplementedError()

    def div(self, term):
        raise NotImplementedError()

    def pow(self, term):
        raise NotImplementedError()

    def log(self, base):
        raise NotImplementedError()


class Equals(Relation):
    """Equality (==) relation."""

    def __init__(self, left: DavidBase | int | float, right: DavidBase | int | float):
        super().__init__(
            internalize(left), '=', internalize(right),

            reflexive=True,
            symmetric=True,
            transitive=True
        )

    def add(self, term):
        ADD_PATTERN = Pattern(Relation.w + term)
        return self.apply(ADD_PATTERN)

    def mul(self, term):
        MUL_PATTERN = Pattern(Relation.w * term)
        return self.apply(MUL_PATTERN)

    def div(self, term):
        DIV_PATTERN = Pattern(Relation.w / term)
        return self.apply(DIV_PATTERN)

    def pow(self, term):
        POW_PATTERN = Pattern(Relation.w ** term)
        return self.apply(POW_PATTERN)

    def log(self, base):
        LOG_PATTERN = Pattern(Log(base, Relation.w))
        return self.apply(LOG_PATTERN)


# TODO Implement add, mul, div, pow, log for all relations

class GreaterThan(Relation):
    """Greater than (>) relation."""

    def __init__(self, left: DavidBase, right: DavidBase):
        super().__init__(
            left, '>', right,

            reflexive=False,
            symmetric=False,
            transitive=True
        )


class LessThan(Relation):
    """Less than (<) relation."""

    def __init__(self, left: DavidBase, right: DavidBase):
        super().__init__(
            left, '<', right,

            reflexive=False,
            symmetric=False,
            transitive=True
        )


class GreaterThanOrEqual(Relation):
    """Greater than or equal to (>=) relation."""

    def __init__(self, left: DavidBase, right: DavidBase):
        super().__init__(
            left, '>=', right,

            reflexive=True,
            symmetric=False,
            transitive=True
        )


class LessThanOrEqual(Relation):
    """Less than or equal to (<=) relation."""

    def __init__(self, left: DavidBase, right: DavidBase):
        super().__init__(
            left, '<=', right,

            reflexive=True,
            symmetric=False,
            transitive=True
        )
