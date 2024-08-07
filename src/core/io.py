from operator import and_, or_, not_


class AssumptionIO:
    """
    | Syntactic sugar for assumption definitions.
    """

    operators = {
        'and': and_,
        'or': or_,
        'not': not_
    }

    def __init__(self, payload):
        self.payload = payload

    def __ge__(self, other: 'AssumptionIO'):
        return 'equiv', self.payload, other.payload

    def __gt__(self, other: 'AssumptionIO'):
        return 'implies', self.payload, other.payload

    def __or__(self, other: 'AssumptionIO'):
        return AssumptionIO(('or', self.payload, other.payload))

    def __ror__(self, other: 'AssumptionIO'):
        return AssumptionIO(('or', other.payload, self.payload))

    def __and__(self, other: 'AssumptionIO'):
        return AssumptionIO(('and', self.payload, other.payload))

    def __rand__(self, other: 'AssumptionIO'):
        return AssumptionIO(('and', other.payload, self.payload))

    def __invert__(self):
        return AssumptionIO(('not', self.payload))


# noinspection PyTypeChecker
# TODO Compound inequalities (a > b > c, avoid compound =)
class RelationIO:
    """| Syntactic sugar for relations."""

    # def __eq__(self, other):
    #     from src.struct.relation import Equals
    #
    #     return Equals(self, other)

    def __eq__(self, other):
        # TODO REQUIRED FOR MAKING THEM HASHABLE, WHAT DO WE DO HERE??
        return hash(self) == hash(other)

    def __gt__(self, other):
        from src.struct.relation import GreaterThan

        return GreaterThan(self, other)

    def __lt__(self, other):
        from src.struct.relation import LessThan

        return LessThan(self, other)

    def __ge__(self, other):
        from src.struct.relation import GreaterThanOrEqual

        return GreaterThanOrEqual(self, other)

    def __le__(self, other):
        from src.struct.relation import LessThanOrEqual

        return LessThanOrEqual(self, other)


class OperatorIO(RelationIO):
    """| Syntactic sugar for operators."""

    # Addition
    
    def __add__(self, other):
        from src.struct.op import Add

        return Add(self, other)

    def __radd__(self, other):
        from src.struct.op import Add

        return Add(other, self)

    # Subtraction & Negation

    def __sub__(self, other):
        from src.struct.op import Add

        return Add(self, -other)

    def __rsub__(self, other):
        from src.struct.op import Add

        return Add(-other, self)

    def __neg__(self):
        from src.struct.op import Multiply

        return Multiply(self, -1)

    # Multiplication

    def __mul__(self, other):
        from src.struct.op import Multiply

        return Multiply(self, other)

    def __rmul__(self, other):
        from src.struct.op import Multiply

        return Multiply(other, self)

    # Division
    # TODO More semantic division? Probably not. But this remains here.

    def __truediv__(self, divisor):
        from src.struct.op import Power, Multiply

        return Multiply(
            self,
            Power(divisor, -1)
        )

    def __rtruediv__(self, dividend):
        from src.struct.op import Power, Multiply

        return Multiply(
            dividend,
            Power(self, -1)
        )

    # Exponentiation

    def __pow__(self, exp):
        from src.struct.op import Power

        return Power(self, exp)

    def __rpow__(self, base):
        from src.struct.op import Power

        return Power(base, self)
