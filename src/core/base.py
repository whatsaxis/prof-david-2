from src.core.assume import Assumption, AssumptionIO, AssumptionSet, EmptyAssumptions

# TODO [https://stackoverflow.com/questions/472000/usage-of-slots]


class DavidBase:
    """| Class for all Professor David objects (assumptions excluded) to derive from."""

    def __init__(self, assumptions: AssumptionSet = None):
        if assumptions is None:
            assumptions = EmptyAssumptions.create()

        self.assumptions = assumptions

    def ask(self, expr: Assumption | AssumptionIO | str | tuple):
        return self.assumptions.ask(expr)

    def copy(self):
        # Stub definition.
        return self

    # TODO die
    def eval(self, *args, **kwargs):
        # Stub definition.
        return self.copy()
