"""An abstract class for an optimiser of binary (on/off) flags"""
from abc import ABC, abstractmethod

from core.flags import Flags
from helpers import Benchmarker, get_random_flag_sample


class FlagOptimiser(ABC):
    """A class to define an optimiser of binary (on/off) flags"""
    fastest_flags: dict[str, bool] = {}
    current_flags: dict[str, bool] = {}
    fastest_time: float
    opt_steps_done: int = 0
    states_explored: int = 0

    def __init__(self, flags: Flags):
        #TODO: Consider changing this to a random choice of flags (defensive flags and completeness)
        self.fastest_flags = get_random_flag_sample(flags)
        self.current_flags = get_random_flag_sample(flags)
        self.fastest_time = float('inf')

    @abstractmethod
    def continuous_optimise(self, benchmarker: Benchmarker) -> dict[str, bool]:
        """
        Optimise the flags continuously until the algorithm is fully finished
        :param benchmarker: The object used to benchmark the code
        :return: The best flags once the algorithm has decided on a global minimum
        """
        raise NotImplementedError

    @abstractmethod
    def n_steps_optimise(self, benchmarker: Benchmarker, n: int) -> dict[str, bool]:
        """
        Optimise the flags for a certain number of optimisation steps
        :param benchmarker: The object used to benchmark the code
        :param n: The number of optimisation steps used
        :return: The best flags after n optimisation steps
        """
        raise NotImplementedError

    @abstractmethod
    def optimisation_step(cls, flags: dict[str, bool]) -> dict[str, bool] | list[dict[str, bool]]:
        """
        Completes a step of the optimisation, returning the flags after the choice is made
        :param flags: A dictionary of flags and their on/off states to optimise
        :return: The flags suggested after the optimisation step
        """
        raise NotImplementedError

    def print_optimisation_info(self):
        print(f"Number of states explored: {self.states_explored}")
        print(f"Fastest time so far: {self.fastest_time}")

    def get_fastest_flags(self) -> dict[str, bool]:
        """Returns the current fastest flags of the optimiser"""
        return self.current_flags
