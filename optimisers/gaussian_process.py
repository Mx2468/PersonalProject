from core.benchmarking import Benchmarker
from core.flags import Flags
from optimisers import FlagOptimiser
class GaussianProcessOptimiser(FlagOptimiser):

    def __init__(self, starting_flags: Flags):
        super().__init__(starting_flags)
        pass

    def optimisation_step(self, flags: dict[str, bool]) -> dict[str, bool] | list[dict[str, bool]]:
        pass

    def n_steps_optimise(self, benchmarker: Benchmarker, n: int) -> dict[str, bool]:
        pass

    def continuous_optimise(self, benchmarker: Benchmarker) -> dict[str, bool]:
        pass
    #TODO: Implement a converter from flag representation to skopt space objects

    #TODO: Plug in skopt objects into gp_minimise
        # TODO:

    #TODO: Create wrapper function for benchmarking code from given sample

