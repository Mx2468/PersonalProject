""" A Module to run and control the running of the flag optimisation"""
import os
from time import time
import subprocess
import flag_reader
import random_search
import sys
import signal


class FlagOptimisationController:
    SOURCE_CODE_FILE = "./test_cases/"
    COMPILED_CODE_FILE = "filetotest"

    def __init__(self, source_code_file: str, compiled_code_name: str = "filetotest"):
        self.SOURCE_CODE_FILE = os.path.join(self.SOURCE_CODE_FILE, source_code_file)
        self.COMPILED_CODE_FILE = compiled_code_name

    def run_compiled_code(self) -> None:
        subprocess.run(f"./{self.COMPILED_CODE_FILE}", shell=True, cwd=os.getcwd())

    def test_compilation_with_flag(self, function_to_benchmark: callable,
                                   opt_flag: str = "O0") -> float:
        subprocess.run(
            [f"g++ {opt_flag} -w -o {self.COMPILED_CODE_FILE} {self.SOURCE_CODE_FILE}"],
            shell=True, cwd=os.getcwd())
        return self.time_needed(3, function_to_benchmark)

    @staticmethod
    def create_flag_string(flag_choices: dict[str, bool]) -> str:
        final_str = ""
        for flag_name, choice in flag_choices.items():
            if choice:
                final_str += f"{flag_name} "
            else:
                # Case where the flag is not chosen
                final_str += f"{flag_name.replace("-f", "-fno-", 1)} "

        return final_str

    @staticmethod
    def time_needed(number_of_repititions: int, function_to_run: callable) -> float:
        """For measuring time"""
        start = time()
        for j in range(0, number_of_repititions):
            function_to_run()
        end = time()
        # time.time returns time in seconds, so conversion is not needed
        return (end - start) / number_of_repititions

    @staticmethod
    def validate_flag_choices(flag_choice: dict[str, bool]) -> dict[str, bool]:
        """Validates that the flags chosen are correct"""
        del flag_choice["-fkeep-inline-dllexport"]  # Not supported by my configuration
        flag_choice["-fsection-anchors"] = flag_choice["-ftoplevel-reorder"] = flag_choice[
            "-funit-at-a-time"]  # Needs to be the same as the others
        return flag_choice

    def opt_loop(self, n: int, flags: list[str]) -> dict[str, bool]:
        """
        Performs n optimisation steps iteratively on the flags passed in

        :param n: Number of optimisation loop iterations to perform
        :param flags: List of flag names to optimise

        :return: Dictionary with the flag names and whether or not they were chosen
        """
        fastest_time = None
        fastest_flags = None
        for i in range(n):
            flag_choice = random_search.random_search(flags)
            validated_flag_choice = self.validate_flag_choices(flag_choice)
            current_time = self.test_compilation_with_flag(self.run_compiled_code,
                                                           opt_flag=self.create_flag_string(
                                                               validated_flag_choice))
            if fastest_time is None or current_time < fastest_time:
                fastest_time = current_time
                fastest_flags = flag_choice
        return fastest_flags

    def anytime_loop(self, flags: list[str]) -> dict[str, bool]:
        """ Runs the optimisation loop until the computation is stopped via ctrl+c"""
        fastest_time = None
        fastest_flags = flags
        states_explored = 0
        def return_results(*args):
            print('You pressed ^C!')
            print(f"States Explored: {states_explored}")
            print(f"Fastest Time: {fastest_time}s")
            print(f"Fastest Flags: {self.create_flag_string(fastest_flags)}")
            sys.exit(0)

        signal.signal(signal.SIGINT, return_results)
        while states_explored < 2 ** 230:
            flag_choice = random_search.random_search(flags)
            validated_flag_choice = self.validate_flag_choices(flag_choice)
            current_time = self.test_compilation_with_flag(self.run_compiled_code,
                                                           opt_flag=self.create_flag_string(
                                                               validated_flag_choice))
            if fastest_time is None or current_time < fastest_time:
                fastest_time = current_time
                fastest_flags = flag_choice

            states_explored += 1
        return fastest_flags


if __name__ == '__main__':
    cont_obj = FlagOptimisationController("BreadthFSSudoku.cpp")
    flags = flag_reader.read_binary_flags()
    # TODO - make a way for this to run indefinite numbers of times/anytime algorithm ( keep the definite number of times if possible just in case)
    result = cont_obj.anytime_loop(flags)
    print(result)
