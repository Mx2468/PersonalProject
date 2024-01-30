""" A class used to implement a random search algorithm for optimising flags """
from random import getrandbits
from optimisers.optimiser import FlagOptimiser
from helpers import validate_flag_choices, create_flag_string, Benchmarker


class RandomSearchOptimiser(FlagOptimiser):
    """ A class for random search optimisation of compiler flags"""
    def __init__(self, flags_to_optimise: list[str]):
        super().__init__(flags_to_optimise)
        self.fastest_time = float('inf')

    def optimisation_step(self, flags: dict[str, bool]):
        return {flag: bool(getrandbits(1)) for flag in flags}

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

    # TODO Implement n-steps optimisation in random search class

    def clear_between_runs(self):
        """ Clears all the lingering state in the class between optimisation runs """
        self.fastest_flags = {}
        self.current_flags = {}
        self.fastest_time = float('inf')
        self.states_explored = 0
