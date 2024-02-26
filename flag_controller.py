"""A Module to run and control the running of the flag optimisation"""
import os

from optimisers import *
import signal
from helpers import constants, Benchmarker

interrupted_handler_executed = False

SOURCE_CODE_FILE = "./test_cases/BreadthFSSudoku.cpp"

class FlagOptimisationController:
    """ A class to orchestrate and control the flag optimisation process"""
    flags: Flags

    def __init__(self,
                 binary_flags_file: str,
                 domain_flags_file: str,
                 source_code_file: str,
                 compiled_code_name: str = constants.COMPILED_CODE_FILE):
        """
        :param binary_flags_file: The path to the file containing the binary choice flags
        :param domain_flags_file: The path to the file containing the domain choice flags
        :param source_code_file: The path to the source code to be compiled
        :param compiled_code_name: A path/name for the intermediate compiled executable file
        (not necessary for most uses - only if the environment rejects the default name)
        """
        self.SOURCE_CODE_FILE = os.path.join(constants.SOURCE_CODE_DIR, source_code_file)
        self.COMPILED_CODE_FILE = compiled_code_name

        flags_obj = Flags()
        flags_obj.load_in_flags(binary_flags_file, domain_flags_file)
        self.flags = flags_obj

    def n_times_optimisation(self,
                             n_steps: int,
                             optimiser: FlagOptimiser,
                             benchmark_obj: Benchmarker) -> dict[str, bool]:
        """
        Run the optimisation for n steps and return the optimal flags after those steps
        :param n_steps: The number of steps to run the simulation for
        :param optimiser: The optimiser object that will be used to optimise the flags
        :param benchmark_obj: The object for benchmarking
        :return: The dictionary of flags and whether they were chosen or not
        """
        optimiser.n_steps_optimise(benchmark_obj, n_steps)
        print('The optimisation process finished')
        print(f"States Explored: {optimiser.states_explored}")
        print(f"Fastest Time: {optimiser.fastest_time}s")
        print(f"Fastest Flags: {create_flag_string(optimiser.fastest_flags)}")

    def anytime_optimisation(self,
                             optimiser: FlagOptimiser,
                             benchmark_obj: Benchmarker) -> dict[str, bool]:
        """
        Runs the optimisation loop until the computation is stopped via ctrl+c,
        then prints out the flags to the user
        :param optimiser: The optimiser object that will be used to optimise the flags
        :param benchmark_obj: The object for benchmarking
        :return The dictionary of flags and whether they were chosen or not
        """
        def return_results(*args) -> None:
            # Global variable used between threads to make sure this message is only printed once
            # (i.e. by only one thread)
            global interrupted_handler_executed
            if not interrupted_handler_executed:
                interrupted_handler_executed = True
                print('You pressed ^C!')
                print(f"States Explored: {optimiser.states_explored}")
                print(f"Fastest Time: {optimiser.fastest_time}s")
                print(f"Fastest Flags: {create_flag_string(optimiser.fastest_flags)}")

        signal.signal(signal.SIGINT, return_results)
        return optimiser.continuous_optimise(benchmark_obj)


    def dump_flags(self, filename: str) -> None:
        pass

#TODO have cli flags control which optimisation method and approach to use (default random search anytime algorithm)
#TODO: Rename "n-step" optimisation to contract algorithm
#TODO: Implement dumping of the flags to a file or stdout at the end of anytime optimisation
#TODO: Implement proper handling of domain flags
#TODO: Change as many class attributes as possible to private
if __name__ == '__main__':
    # SOURCE_CODE_FILE = os.path.join(constants.SOURCE_CODE_DIR, "BreadthFSSudoku.cpp")
    controller = FlagOptimisationController("flags/binary_flags.txt",
                                            "flags/domain_flags.json",
                                            SOURCE_CODE_FILE)

    benchmarker = Benchmarker(SOURCE_CODE_FILE)
    random_flags = validate_flag_choices(get_random_flag_sample(controller.flags))
    default_flag_str = create_flag_string(random_flags)
    benchmarker.compare_with_o3(default_flag_str)

    # optimiser = GeneticAlgorithmOptimiser(controller.flags, 10, [o3_flags_choice])
    # controller.anytime_optimisation(optimiser, benchmarker)
