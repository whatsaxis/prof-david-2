from typing import Optional, Type

from src.core.base import DavidBase
from src.core.assume import NumberAssumptions
from src.core.io import OperatorIO


class Unknown(DavidBase, OperatorIO):
    """A symbolic unknown variable."""

    def __init__(self, symbol: str, **facts):
        super().__init__(NumberAssumptions.create(**facts))

        self.symbol = symbol

    def __hash__(self):
        return hash(self.symbol)

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return str(self)


class Wild(DavidBase, OperatorIO):
    """Wildcard matching object for patterns."""

    def __init__(self, symbol: str, *, sequence=False):
        # TODO Make an assumption set for Wild()
        # TODO Should Wild() inherit from unknown?
        super().__init__()

        self.symbol = symbol

        # TODO This here or in the Pattern object?
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
