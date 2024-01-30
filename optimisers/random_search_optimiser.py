""" A class used to implement a random search algorithm for optimising flags """
from random import getrandbits
from optimisers.optimiser import FlagOptimiser
from utilities import validate_flag_choices, benchmark_flag_choices, create_flag_string
from utilities.constants import SOURCE_CODE_FILE, COMPILED_CODE_FILE


class RandomSearchOptimiser(FlagOptimiser):
    """ A class for random search optimisation of compiler flags"""
    def __init__(self, flags_to_optimise: list[str]):
        super().__init__()
        self.fastest_flags = {flag: False for flag in flags_to_optimise}
        self.current_flags = {flag: False for flag in flags_to_optimise}
        self.fastest_time = None

    def optimisation_step(self, flags: dict[str, bool]):
        return {flag: bool(getrandbits(1)) for flag in flags}

    def optimise(self, flags_to_optimise: dict[str, bool]) -> dict[str, bool]:
        # Explores the state space until it is done (as part of an anytime algorithm)
        while self.states_explored < 2 ** len(flags_to_optimise.keys()):
            # Get next optimisation flags
            self.current_flags = self.optimisation_step(flags_to_optimise)
            validated_flag_choices = validate_flag_choices(self.current_flags)
            current_time = benchmark_flag_choices(
                SOURCE_CODE_FILE,
                COMPILED_CODE_FILE,
                opt_flag=create_flag_string(validated_flag_choices))

            if self.fastest_time is None or current_time < self.fastest_time:
                self.fastest_time = current_time
                self.fastest_flags = self.current_flags

            self.states_explored += 1

        # Clean up class for next opt run before returning flags
        flags_to_return = self.fastest_flags
        self.clear_between_runs()
        return flags_to_return

    def clear_between_runs(self):
        """ Clears all the lingering state in the class between optimisation runs """
        self.fastest_flags = {}
        self.current_flags = {}
        self.fastest_time = None
        self.states_explored = 0
