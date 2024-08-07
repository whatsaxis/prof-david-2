class DavidIsAngry(Exception):
    """Base exception class for Professor David."""

    pass


"""Assumptions"""


class AssumptionError(DavidIsAngry):
    """Base error for the assumption system."""

    pass


class InvalidImplication(AssumptionError):
    """
    | Thrown when:
    |
    | - Attempting to use a standalone statement as a predicate
    | - Attempting to imply a compound statement as opposed to another assumption (or the ``NOT`` of that assumption).
    """

    pass


class Contradiction(AssumptionError):
    """
    | Occurs when there is a contradiction between assumptions.
    | This is a special type of exception, as it can also be thrown when things are going right!
    """

    pass
