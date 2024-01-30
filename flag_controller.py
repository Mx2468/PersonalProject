""" A Module to run and control the running of the flag optimisation"""
import os

from optimisers.optimiser import FlagOptimiser
from optimisers.random_search import RandomSearchOptimiser
import sys
import signal

from helpers import create_flag_string, constants, Benchmarker
from reader.binary_flag_reader import BinaryFlagReader


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

    #TODO Move below code to optimiser for n-step optimisation

    # def opt_loop(self, n: int, ) -> dict[str, bool]:
    #     """
    #     Performs n optimisation steps iteratively on the flags passed in
    #
    #     :param n: Number of optimisation loop iterations to perform
    #     :param flags_to_optimise: List of flag names to optimise
    #
    #     :return: Dictionary with optimal flag combination.
    #     """
    #     fastest_time = None
    #     fastest_flags = None
    #     for i in range(n):
    #         flag_choice = random_search.random_search(flags_to_optimise)
    #         validated_flag_choice = validate_flag_choices(flag_choice)
    #         current_time = benchmarking.benchmark_flag_choices(
    #             source_code_file_name=self.SOURCE_CODE_FILE,
    #             compiled_file_name=self.COMPILED_CODE_FILE,
    #             opt_flag=create_flag_string(validated_flag_choice))
    #         if fastest_time is None or current_time < fastest_time:
    #             fastest_time = current_time
    #             fastest_flags = flag_choice
    #     return fastest_flags

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


#TODO move this behaviour into functions seperated by n-step and anytime optimisation
#TODO have cli flags control which optimisation method and approach to use (default random search anytime algorithm)
if __name__ == '__main__':
    SOURCE_CODE_FILE = os.path.join(constants.SOURCE_CODE_DIR, "BreadthFSSudoku.cpp")
    controller = FlagOptimisationController("binary_flags.txt", SOURCE_CODE_FILE)
    optimiser = RandomSearchOptimiser(controller.flags)
    benchmarker = Benchmarker(SOURCE_CODE_FILE)

    # Runs optimisation until user stops execution with ctrl+c
    controller.anytime_optimisation(optimiser, benchmarker)
