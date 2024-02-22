""" A Module to run and control the running of the flag optimisation"""
import os

from optimisers import *
import sys
import signal

from helpers import constants, Benchmarker
from reader.binary_flag_reader import BinaryFlagReader

#TODO: refactor flags paths

class FlagOptimisationController:
    """ A class to orchestrate and control the flag optimisation process"""
    COMPILED_CODE_FILE = "filetotest"

    def __init__(self, flags_file: str, source_code_file: str, compiled_code_name: str = "filetotest"):
        """
        :param flags_file: The path to the file containing the flags
        :param source_code_file: The path to the source code to be compiled
        :param compiled_code_name: A path/name for the intermediate compiled executable file
        (not necessary for most uses - only if the environment rejects the default name)
        """
        self.SOURCE_CODE_FILE = os.path.join(constants.SOURCE_CODE_DIR, source_code_file)
        self.COMPILED_CODE_FILE = compiled_code_name

        # Currently only reads in binary flags
        with BinaryFlagReader(flags_file) as flag_reader:
            flag_reader.read_in_flags()
            self.flags = flag_reader.get_flags()

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
            print('You pressed ^C!')
            print(f"States Explored: {optimiser.states_explored}")
            print(f"Fastest Time: {optimiser.fastest_time}s")
            print(f"Fastest Flags: {create_flag_string(optimiser.fastest_flags)}")
            sys.exit(0)

        signal.signal(signal.SIGINT, return_results)
        return optimiser.continuous_optimise(benchmark_obj)


#TODO have cli flags control which optimisation method and approach to use (default random search anytime algorithm)
#TODO: Rename "n-step" optimisation to contract algorithm
#TODO: Implement dumping of the flags to a file or stdout at the end of anytime optimisation
if __name__ == '__main__':
    SOURCE_CODE_FILE = os.path.join(constants.SOURCE_CODE_DIR, "BreadthFSSudoku.cpp")
    controller = FlagOptimisationController("flags/binary_flags.txt", SOURCE_CODE_FILE)

    o3_flags: dict[str, bool] = None
    with BinaryFlagReader("./flags/O3_flags.txt") as o3_flags_reader:
        o3_flags_reader.read_in_flags()
        o3_flags = o3_flags_reader.get_flags()
    o3_flags_choice = {name: True for name in o3_flags}

    optimiser = GeneticAlgorithmOptimiser(controller.flags, 4, [o3_flags_choice])
    benchmarker = Benchmarker(SOURCE_CODE_FILE)
    # Runs optimisation until user stops execution with ctrl+c
    #controller.n_times_optimisation(20, optimiser, benchmarker)
    controller.anytime_optimisation(optimiser, benchmarker)
    benchmarker.compare_with_o3(create_flag_string(optimiser.get_fastest_flags()))
    # random_flags = validate_flag_choices(get_random_flag_sample(controller.flags))
    # print(benchmarker.parallel_benchmark_flags(create_flag_string(random_flags), 10))
