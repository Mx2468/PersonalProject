""" A class used to implement a random search algorithm for optimising flags"""

import helpers
from core.flags import Flags
from optimisers.optimiser import FlagOptimiser
from core.benchmarking import Benchmarker
from core.validation import validate_flag_choices
from helpers import create_flag_string


class RandomSearchOptimiser(FlagOptimiser):
    """A class for random search optimisation of compiler flags"""
    def __init__(self, flags_to_optimise: Flags):
        super().__init__(flags_to_optimise)
        self.__flags_object = flags_to_optimise

    def get_random_flags(self) -> dict[str, bool]:
        """Returns a random validated choice of flags, ready for compilation"""
        return validate_flag_choices(helpers.get_random_flag_sample(self.__flags_object))

    def continuous_optimise(self, benchmark_obj: Benchmarker) -> dict[str, bool]:
        # Explores the state space until it is done (as part of an anytime algorithm)
        while self._states_explored < 2 ** len(self._current_flags.keys()):
            self.optimisation_step(benchmark_obj)

        # Clean up class for next optimisation run before returning flags
        return self._fastest_flags

    def n_steps_optimise(self, benchmark_obj: Benchmarker, n: int) -> dict[str, bool]:
        for i in range(n):
            self.optimisation_step(benchmark_obj)

        # Clean up class for next optimisation run before returning flags
        return self._fastest_flags

    def optimisation_step(self, benchmark_obj: Benchmarker) -> None:
        """
        Completes an optimisation step - recording the fastest flags other info after each optimisation step

        :param benchmark_obj: The `Benchmarker` object used to benchmark the code
        """
        self._current_flags = self.get_random_flags()

        validated_flag_choice = validate_flag_choices(self._current_flags)
        current_time = benchmark_obj.benchmark_flag_choices(
            opt_flag=create_flag_string(validated_flag_choice))

        if self._fastest_time is None or current_time < self._fastest_time:
            self._fastest_time = current_time
            self._fastest_flags = self._current_flags

        self._states_explored += 1
        self._opt_steps_done += 1
        self.print_optimisation_info()


    def _clear_between_runs(self):
        """Clears all the lingering state in the class between optimisation runs"""
        self._fastest_flags = {}
        self._current_flags = {}
        self._fastest_time = float('inf')
        self._states_explored = 0
