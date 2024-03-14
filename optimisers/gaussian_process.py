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
        super().__init__(all_flags)
        self.flags_obj = all_flags
        flag_domain_mapping = self.flags_obj.get_all_flag_domains()
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
                             acq_optimizer="auto",
                             verbose=True)
        if self._fastest_time > result.fun:
            self._fastest_time = result.fun
            self._fastest_flags = validate_flag_choices(self._convert_to_flag_choice(result.x))
        return self._fastest_flags

    def continuous_optimise(self, benchmarker: Benchmarker) -> dict[str, bool]:
        print("Continuous optimisation is not currently possible with this algorithm - setting up a 1000 step optimisation run")
        return self.n_steps_optimise(benchmarker, 1000)

    def optimisation_step(cls, flags: dict[str, bool]) -> dict[str, bool] | list[dict[str, bool]]:
        pass

    def _convert_to_flag_choice(self, argument: list[str | int | bool]) -> dict[str, str | bool]:
        flag_choice = {}
        for index, value in enumerate(argument, 0):
            flag_name = self._flags_in_order_of_domain[index]
            if self._domains[index] == Categorical([True, False]):
                flag_choice[flag_name] = bool(value)
            else:
                flag_choice[flag_name] = str(value)

        return flag_choice

    def runner_wrapper_function(self, *args) -> float:
        # Convert args to a set of flag choices
        choice = self._convert_to_flag_choice(*args)
        # Validate flag choices
        validated_choice = validate_flag_choices(choice)
        # Run code given args argument
        return self.benchmarker.parallel_benchmark_flags(create_flag_string(validated_choice))