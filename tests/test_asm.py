import pytest

from src.core.assume import Assumption, AssumptionSet
from src.core.error import InvalidImplication, Contradiction


A, B, C, D, E, F = map(Assumption, ('A', 'B', 'C', 'D', 'E', 'F'))


def test_eq():

    # Simple equivalence
    assert AssumptionSet(
        B <= A,
        A=True
    ).ask(B) is True

    assert AssumptionSet(
        B <= A,
        A=False
    ).ask(B) is False

    # Compound equivalence
    assert AssumptionSet(
        B <= A,
        D <= B & C,

        A=True, C=True
    ).ask(D) is True

    assert AssumptionSet(
        D <= (A | B) & C,
        E <= ~D,

        A=False, B=True, C=True
    ).ask(E) is False

    # Chained equivalence (ordered)
    assert AssumptionSet(
        B <= A,
        C <= B,
        D <= C,
        A=True
    ).ask(D) is True

    assert AssumptionSet(
        B <= A,
        C <= B,
        D <= C,
        A=False
    ).ask(D) is False

    # Chained equivalence (not ordered)
    assert AssumptionSet(
        C <= B,
        D <= C,
        B <= A,
        A=True
    ).ask(D) is True

    assert AssumptionSet(
        C <= B,
        D <= C,
        B <= A,
        A=False
    ).ask(D) is False


def test_imply():

    # Simple implications
    assert AssumptionSet(
        A > B,
        A=True
    ).ask(B) is True

    assert AssumptionSet(
        A > B,
        A=False
    ).ask(B) is None

    # Compound implication

    assert AssumptionSet(
        (A & B) | C > D,
        C=True
    ).ask(D) is True

    assert AssumptionSet(
        A | B | C | D | E | F > D,
        A=False, B=False, C=False, E=True, F=False
    ).ask(D) is True

    # Chained implication (ordered)
    assert AssumptionSet(
        (A & B) | C > D,
        D > ~E,
        C=True
    ).ask(E) is False

    assert AssumptionSet(
        ~A > B,
        B > ~D,
        A=False
    ).ask(D) is False

    # Chained implications (not ordered)

    assert AssumptionSet(
        D > E,
        C > D,
        A > B,
        B > C,
        E > ~F,
        D=True
    ).ask(F) is False

    assert AssumptionSet(
        D > E,
        C > D,
        A > B,
        B > C,
        E > ~F,
        D=True
    ).ask(A) is None


def test_error():

    # Invalid predicates
    with pytest.raises(InvalidImplication):
        AssumptionSet(
            A
        )

    with pytest.raises(InvalidImplication):
        AssumptionSet(
            A | B & C & D,
            A <= E | F
        )

    # Contradictions
    with pytest.raises(Contradiction):
        AssumptionSet(
            ~A <= A,
            A=True
        )

    with pytest.raises(Contradiction):
        AssumptionSet(
            B <= A,
            ~A <= B,
            A=True
        )

    with pytest.raises(Contradiction):
        AssumptionSet(
            (A & B) | C > D,
            D > ~E,
            D <= E,
            C=True
        )
