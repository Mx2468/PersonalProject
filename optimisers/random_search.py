""" A class used to implement a random search algorithm for optimising flags """
import helpers
from optimisers.optimiser import FlagOptimiser
from helpers import validate_flag_choices, create_flag_string, Benchmarker


class RandomSearchOptimiser(FlagOptimiser):
    """ A class for random search optimisation of compiler flags"""
    def __init__(self, flags_to_optimise: list[str]):
        super().__init__(flags_to_optimise)

    def optimisation_step(self, flags: dict[str, bool]) -> dict[str, bool]:
        return validate_flag_choices(helpers.get_random_flag_sample(list(flags.keys())))

    def continuous_optimise(self, benchmark_obj: Benchmarker) -> dict[str, bool]:
        # Explores the state space until it is done (as part of an anytime algorithm)
        while self.states_explored < 2 ** len(self.current_flags.keys()):

            # Get next optimisation flags
            self.current_flags = self.optimisation_step(self.current_flags)

            # Validate & benchmark next flags
            validated_flag_choices = validate_flag_choices(self.current_flags)
            current_time = benchmark_obj.benchmark_flag_choices(
                opt_flag=create_flag_string(validated_flag_choices))

            # Check & record improvement
            if self.fastest_time is None or current_time < self.fastest_time:
                self.fastest_time = current_time
                self.fastest_flags = self.current_flags

            self.states_explored += 1

        # Clean up class for next optimisation run before returning flags
        flags_to_return = self.fastest_flags
        self.clear_between_runs()
        return flags_to_return

    def n_steps_optimise(self, benchmark_obj: Benchmarker, n: int) -> dict[str, bool]:
        """
        Performs n optimisation steps iteratively on the flags passed in

        :param n: Number of optimisation loop iterations to perform
        :param flags_to_optimise: List of flag names to optimise

        :return: Dictionary with optimal flag combination.
        """
        for i in range(n):
            self.current_flags = self.optimisation_step(self.current_flags)

            validated_flag_choice = validate_flag_choices(self.current_flags)
            current_time = benchmark_obj.benchmark_flag_choices(
                opt_flag=create_flag_string(validated_flag_choice))

            if self.fastest_time is None or current_time < self.fastest_time:
                self.fastest_time = current_time
                self.fastest_flags = self.current_flags

        # Clean up class for next optimisation run before returning flags
        flags_to_return = self.fastest_flags
        self.clear_between_runs()
        return flags_to_return
    def n_steps_optimise(self, benchmarker: Benchmarker, n: int) -> dict[str, bool]:
        for i in range(n):
            self.current_flags = self.optimisation_step(self.current_flags)

            current_time = benchmarker.benchmark_flag_choices(
                opt_flag=create_flag_string(self.current_flags))

            if self.fastest_time is None or current_time < self.fastest_time:
                self.fastest_time = current_time
                self.fastest_flags = self.current_flags

            self.states_explored += 1

        return self.fastest_flags


    def clear_between_runs(self):
        """ Clears all the lingering state in the class between optimisation runs """
        self.fastest_flags = {}
        self.current_flags = {}
        self.fastest_time = float('inf')
        self.states_explored = 0
