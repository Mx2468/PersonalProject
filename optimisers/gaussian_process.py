"""
A class implementing the `skopt` `gp_minimize` function as a
gaussian process optimizer for optimisation flags
"""
from random import getrandbits

from skopt import Optimizer
from skopt.space import Categorical

from core.benchmarking import Benchmarker
from core.flags import Flags
from core.validation import validate_flag_choices
from helpers import create_flag_string, helpers
from optimisers import FlagOptimiser
import helpers.constants as constants
import optimisers.config.gaussian_process_config as configuration

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
                    self._domains.append((1, 19))
                else:
                    self._domains.append((0, constants.INTEGER_DOMAIN_UPPER_BOUND))
            elif domain == [True, False]:
                self._domains.append(Categorical(categories=(True, False), prior=None))
            else:
                self._domains.append(tuple(domain))
            self._flags_in_order_of_domain.append(flag)

        if starting_flags:
            self.starting_flags = starting_flags
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
        else:
            self.starting_flags = None
            self.x = None
            self.y = None

    def convert_to_skopt(self, validated_flag_comb: dict[str, str|bool]):
        x = []
        for flag in self._flags_in_order_of_domain:
            value = validated_flag_comb[flag]
            x.append(self.convert_value_to_skopt(flag, value))

        return x

    def convert_value_to_skopt(self, flag_name: str, value: str):
        domain = self.flags_obj.get_flag_domain(flag_name)
        match domain:
            case "Integer":
                return int(value)
            case "Integer-or-binary":
                if isinstance(value, int):
                    return int(value)
                else:
                    return bool(value)
            case "Integer-align":
                return int(value)
            case [*domain_values]:
                # Special case for live-patching
                if flag_name == "-flive-patching":
                    if isinstance(value, bool):
                        return False
                    else:
                        return str(value)
                if isinstance(value, bool):
                    return bool(value)
                else:
                    return str(value)
            case _:
                raise ValueError(f"Unrecognised flag domain {domain} for flag {flag_name}")


    def evaluate_starting_flags(self):
        # Evaluate starting flags
        if self.starting_flags:
            for flag_comb in self.starting_flags:
                validated_flag_comb = validate_flag_choices(flag_comb)
                current_time = self.benchmarker.parallel_benchmark_flags(
                    create_flag_string(validated_flag_comb))
                if current_time < self._fastest_time:
                    self._fastest_flags = flag_comb
                    self._fastest_time = current_time
                skopt_converted_x = self.convert_to_skopt(validated_flag_comb)
                print(validated_flag_comb)
                print(self._domains)
                print(skopt_converted_x)
                self._optimizer_obj.tell(skopt_converted_x, current_time, fit=True)


    def _create_necessary_objects(self, benchmarker: Benchmarker) -> None:
        self.benchmarker = benchmarker
        self._optimizer_obj = Optimizer(dimensions=self._domains,
                  n_initial_points=configuration.N_INITIAL_POINTS,
                  initial_point_generator=configuration.INITIAL_POINT_GENERATOR_METHOD,
                  acq_func=configuration.ACQUISITION_FUNCTION,
                  acq_optimizer=configuration.ACQUISITION_OPTIMISATION_METHOD,
                  n_jobs=-1)

    def n_steps_optimise(self, benchmarker: Benchmarker, n: int) -> dict[str, bool | str]:
        self._create_necessary_objects(benchmarker)
        self.evaluate_starting_flags()
        for i in range(n):
            self.optimisation_step()
        return self._fastest_flags

    def continuous_optimise(self, benchmarker: Benchmarker) -> dict[str, bool | str]:
        self._create_necessary_objects(benchmarker)
        self.evaluate_starting_flags()
        while self._states_explored < 2 ** len(self._current_flags.keys()):
            self._current_flags = self.optimisation_step()
        return self._fastest_flags

    def optimisation_step(self, flags: dict[str, bool] = None) -> dict[str, bool] | list[dict[str, bool]]:
        result = self._optimizer_obj.run(self.runner_wrapper_function)
        self._states_explored += 1
        self._opt_steps_done += 1
        if self._fastest_time > result.fun:
            self._fastest_time = result.fun
            self._fastest_flags = validate_flag_choices(self._convert_to_flag_choice(result.x))
        self.print_optimisation_info()
        return self._fastest_flags

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

    def _convert_to_skopt_domain(self, flag_choice: dict[str, str | bool]) -> list[str | int | bool]:
        pass

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