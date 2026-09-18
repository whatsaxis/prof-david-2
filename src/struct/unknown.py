from typing import Optional, Type

from src.core.base import DavidBase
from src.core.assume import NumberAssumptions
from src.core.io import OperatorIO


class Unknown(DavidBase, OperatorIO):
    """A symbolic unknown variable."""

    def __init__(self, symbol: str, subscript: str = None, **facts):
        super().__init__(NumberAssumptions.create(**facts))

        self.symbol = symbol
        self.subscript = subscript

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        if self.subscript:
            return f'{ self.symbol }_{ self.subscript }'
        return self.symbol

    def __repr__(self):
        return str(self)


class Wild(DavidBase, OperatorIO):
    """
    Wildcard matching object for patterns.

    ``sequence=True`` creates a sequence wild.
    This matches multiple terms in an operator.
    It matches greedily, so that it has as many terms as possible.
    """

    def __init__(self, symbol: str, *, sequence=False):
        # TODO Make an assumption set for Wild()
        # TODO Should Wild() inherit from unknown?
        super().__init__()

        self.symbol = symbol

        self.sequence = sequence

    def __hash__(self):
        # TODO Test hash-based. Just putting this in here in case you forget.
        return hash(self.symbol)

    def __str__(self):
        if not self.sequence:
            return f'〈{ self.symbol }〉'

        return f'《{ self.symbol }》'

    def __repr__(self):
        return str(self)
