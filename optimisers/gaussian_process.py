import numpy as np
import numpy.array_api
from skopt import gp_minimize
from skopt import load
from skopt.callbacks import CheckpointSaver

from core.benchmarking import Benchmarker
from core.flags import Flags
from core.validation import validate_flag_choices
from helpers import create_flag_string
from optimisers import FlagOptimiser
import helpers.constants as constants

class GaussianProcessOptimiser(FlagOptimiser):

    benchmarker: Benchmarker
    def __init__(self, starting_flags: Flags):
        super().__init__(starting_flags)
        self.flags_obj = starting_flags
        flag_domain_mapping = self.flags_obj.get_all_flag_domains()
        self._domains = []
        self._flags_in_order_of_domain = []

        # Create list of domains and corresponding list of flags in the same order
        for flag, domain in flag_domain_mapping.items():
            if domain == "Integer" or domain == "Integer-align" or domain == "Integer-or-binary":
                self._domains.append((0, constants.INTEGER_DOMAIN_UPPER_BOUND))
            else:
                self._domains.append(tuple(domain))
            self._flags_in_order_of_domain.append(flag)
        print(self._domains)

    def optimisation_step(self, flags: dict[str, bool]) -> dict[str, bool] | list[dict[str, bool]]:
        # Save each evaluation for each choice - give to optimiser as x0 and y0
        pass

    def continuous_optimise(self, benchmarker: Benchmarker) -> dict[str, bool]:
        self.benchmarker = benchmarker
        checkpoint_saver = CheckpointSaver("./checkpoint.pkl", compress=9)
        pass
    def n_steps_optimise(self, benchmarker: Benchmarker, n: int) -> dict[str, bool|str]:
        self.benchmarker = benchmarker
        result = gp_minimize(func=self.runner_wrapper_function,
                          dimensions=self._domains,
                          n_calls=n)

        self._fastest_time = result.fun
        self._fastest_flags = validate_flag_choices(self._convert_to_flag_choice(result.x))

        return self._fastest_flags

    def _convert_to_flag_choice(self, argument: list[str | int | bool]) -> dict[str, str | bool]:
        flag_choice = {}
        for index, value in enumerate(argument, 0):
            flag_name = self._flags_in_order_of_domain[index]
            match type(value):
                case np.bool_:
                    flag_choice[flag_name] = bool(value)
                case numpy.int64:
                    flag_choice[flag_name] = str(value)
                case _:
                    flag_choice[flag_name] = value

        return flag_choice

    def runner_wrapper_function(self, *args) -> float:
        # Convert args to a set of flag choices
        choice = self._convert_to_flag_choice(*args)
        # Validate flag choices
        validated_choice = validate_flag_choices(choice)
        # Run code given args argument
        return self.benchmarker.benchmark_flag_choices(create_flag_string(validated_choice))


#
# noise_level = 0.1
#
#
# def obj_fun(x, noise_level=noise_level):
#     return np.sin(5 * x[0]) * (1 - np.tanh(x[0] ** 2)) + np.random.randn() \
#         * noise_level
#
#
#
#
# if __name__ == "__main__":
#     try:
#         gp_minimize(obj_fun,  # the function to minimize
#                     [(-20.0, 20.0)],  # the bounds on each dimension of x
#                     x0=[-20.],  # the starting point
#                     acq_func="LCB",  # the acquisition function (optional)
#                     n_calls=10,  # number of evaluations of f including at x0
#                     n_random_starts=3,  # the number of random initial points
#                     callback=[checkpoint_saver],
#                     # a list of callbacks including the checkpoint saver
#                     random_state=777)
#     except KeyboardInterrupt:
#         res = load('./checkpoint.pkl')
#         print(res.fun)