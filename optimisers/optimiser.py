"""An abstract class for an optimiser of binary (on/off) flags"""
from abc import ABC, abstractmethod
from helpers import Benchmarker


class FlagOptimiser(ABC):
    """A class to define an optimiser of binary (on/off) flags"""
    fastest_flags: dict[str, bool] = {}
    current_flags: dict[str, bool] = {}
    fastest_time: float
    states_explored: int = 0

    def __init__(self, flags: list[str]):
        self.fastest_flags = {flag: False for flag in flags}
        self.current_flags = {flag: False for flag in flags}
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

    def get_fastest_flags(self) -> dict[str, bool]:
        """Returns the current fastest flags of the optimiser"""
        return self.current_flags
