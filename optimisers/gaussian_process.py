"""
A class implementing the `skopt` `gp_minimize` function as a
gaussian process optimizer for optimisation flags
"""
from skopt import gp_minimize
from skopt.space import Categorical

from core.benchmarking import Benchmarker
from core.flags import Flags
from core.validation import validate_flag_choices
from helpers import create_flag_string
from optimisers import FlagOptimiser
import helpers.constants as constants

class GaussianProcessOptimiser(FlagOptimiser):

    benchmarker: Benchmarker = None
    def __init__(self, all_flags: Flags, starting_flags: list[dict[str, str|bool]]):
        """
        :param all_flags: A `Flags` object containing all flags to optimise
        :param starting_flags: A list of flag choices
        (dictionaries mapping flag names to their corresponding chosen values)
        """
        super().__init__(all_flags)
        self.flags_obj = all_flags
        flag_domain_mapping = self.flags_obj.get_all_flag_domains()

        # Removes flags that are problematic or have difficult domains to optimise
        flag_domain_mapping.pop("-fkeep-inline-dllexport")
        flag_domain_mapping.pop("-ffat-lto-objects")
        flag_domain_mapping.pop("-flive-patching")

        self._domains = []
        self._flags_in_order_of_domain = []

        # Create list of domains and corresponding list of flags in the same order
        for flag, domain in flag_domain_mapping.items():
            if domain == "Integer" or domain == "Integer-align" or domain == "Integer-or-binary":
                if flag == "-flto":
                    self._domains.append((1, constants.INTEGER_DOMAIN_UPPER_BOUND))
                else:
                    self._domains.append((0, constants.INTEGER_DOMAIN_UPPER_BOUND))
            elif domain == [True, False]:
                self._domains.append(Categorical(categories=(True, False), prior=None))
            else:
                self._domains.append(tuple(domain))
            self._flags_in_order_of_domain.append(flag)

        self.x = [[]]
        self.y = None
        for set_of_flags in starting_flags:
            for i, flag in enumerate(self._flags_in_order_of_domain, 0):
                value = set_of_flags[flag]
                try:
                    int_val = int(value)
                    self.x[0].append(int_val)
                except TypeError:
                    self.x[0].append(value)
                except ValueError:
                    self.x[0].append(value)

    def n_steps_optimise(self, benchmarker: Benchmarker, n: int) -> dict[str, bool|str]:
        self.benchmarker = benchmarker
        result = gp_minimize(func=self.runner_wrapper_function,
                             dimensions=self._domains,
                             x0=self.x,
                             y0=self.y,
                             n_calls=n,
                             n_points=n//10,
                             initial_point_generator="lhs",
                             acq_optimizer="auto",
                             noise="gaussian",
                             verbose=True)
        if self._fastest_time > result.fun:
            self._fastest_time = result.fun
            self._fastest_flags = validate_flag_choices(self._convert_to_flag_choice(result.x))
        return self._fastest_flags

    def continuous_optimise(self, benchmarker: Benchmarker) -> dict[str, bool]:
        """Currently a wrapper for a long contract optimisation run"""
        print("Continuous optimisation is not currently possible with this algorithm - setting up a 1000 step optimisation run")
        return self.n_steps_optimise(benchmarker, 1000)

    def optimisation_step(cls, flags: dict[str, bool]) -> dict[str, bool] | list[dict[str, bool]]:
        pass

    def _convert_to_flag_choice(self, argument: list[str | int | bool]) -> dict[str, str | bool]:
        """
        Converts a list of arguments into a flag choice representation used by the rest of the program
        :param argument: A list of values corresponding to flag/flag parameter choices for a flag,
        in the order the flags were specified to the `gp_minimize` function
        :return: A dictionary mapping the flag string to it's corresponding value
        """
        flag_choice = {}
        for index, value in enumerate(argument, 0):
            flag_name = self._flags_in_order_of_domain[index]
            if self._domains[index] == Categorical([True, False]):
                flag_choice[flag_name] = bool(value)
            else:
                flag_choice[flag_name] = str(value)

        return flag_choice

    def runner_wrapper_function(self, *args) -> float:
        """
        A wrapper function to run and benchmark the flag choice provided by the gp_minimise function
        :param args: A list containing the flag choice provided by the gp_minimise function,
        in the order the dimensions where initially specified
        :return: A float representing the benchmarked time of the flags
        """
        # Convert args to a set of flag choices
        choice = self._convert_to_flag_choice(*args)
        # Validate flag choices
        validated_choice = validate_flag_choices(choice)
        # Run code given args argument
        return self.benchmarker.parallel_benchmark_flags(create_flag_string(validated_choice))