""" A Module to run and control the running of the flag optimisation"""
import os
import flag_reader
import random_search
import sys
import signal

from utilities import benchmarking, create_flag_string, validate_flag_choices


class FlagOptimisationController:
    """ A class to orchestrate and control the flag optimisation process"""
    SOURCE_CODE_FILE = "./test_cases/"
    COMPILED_CODE_FILE = "filetotest"

    def __init__(self, source_code_file: str, compiled_code_name: str = "filetotest"):
        """

        :param source_code_file: The path to the source code to be compiled
        :param compiled_code_name: A path/name for the intermediate compiled executable file
        (not necessary for most uses - only if the environment rejects the default name)
        """
        self.SOURCE_CODE_FILE = os.path.join(self.SOURCE_CODE_FILE, source_code_file)
        self.COMPILED_CODE_FILE = compiled_code_name

    def opt_loop(self, n: int, flags_to_optimise: list[str]) -> dict[str, bool]:
        """
        Performs n optimisation steps iteratively on the flags passed in

        :param n: Number of optimisation loop iterations to perform
        :param flags_to_optimise: List of flag names to optimise

        :return: Dictionary with optimal flag combination.
        """
        fastest_time = None
        fastest_flags = None
        for i in range(n):
            flag_choice = random_search.random_search(flags_to_optimise)
            validated_flag_choice = validate_flag_choices(flag_choice)
            current_time = benchmarking.benchmark_flag_choices(
                source_code_file_name=self.SOURCE_CODE_FILE,
                compiled_file_name=self.COMPILED_CODE_FILE,
                opt_flag=create_flag_string(validated_flag_choice))
            if fastest_time is None or current_time < fastest_time:
                fastest_time = current_time
                fastest_flags = flag_choice
        return fastest_flags

    def anytime_loop(self, flags_to_optimise: list[str]) -> dict[str, bool]:
        """ Runs the optimisation loop until the computation is stopped via ctrl+c"""
        fastest_time = None
        fastest_flags = flags_to_optimise
        states_explored = 0
        def return_results(*args):
            print('You pressed ^C!')
            print(f"States Explored: {states_explored}")
            print(f"Fastest Time: {fastest_time}s")
            print(f"Fastest Flags: {create_flag_string(fastest_flags)}")
            sys.exit(0)

        signal.signal(signal.SIGINT, return_results)
        while states_explored < 2 ** 230:
            flag_choice = random_search.random_search(flags_to_optimise)
            validated_flag_choice = validate_flag_choices(flag_choice)
            current_time = benchmarking.benchmark_flag_choices(
                self.SOURCE_CODE_FILE,
                self.COMPILED_CODE_FILE,
                opt_flag=create_flag_string(validated_flag_choice))
            if fastest_time is None or current_time < fastest_time:
                fastest_time = current_time
                fastest_flags = flag_choice

            states_explored += 1
        return fastest_flags


if __name__ == '__main__':
    cont_obj = FlagOptimisationController("BreadthFSSudoku.cpp")
    flags = flag_reader.read_binary_flags()
    result = cont_obj.anytime_loop(flags)
    print(result)
