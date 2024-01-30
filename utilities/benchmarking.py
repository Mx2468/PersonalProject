""" Helper methods that benchmark a set of flags"""

from time import time
import subprocess
import os


DEFAULT_COMPILED_FILE_NAME = "filetotest"


def compile_with_flags(source_code_file: str,
                       compiled_file_name: str = DEFAULT_COMPILED_FILE_NAME,
                       opt_flag: str = "O0"):
    """Compile a c++ source code file with the specified flags"""
    subprocess.run(
        [f"g++ {opt_flag} -w -o {compiled_file_name} {source_code_file}"],
        shell=True, cwd=os.getcwd())


def benchmark_flag_choices(source_code_file_name: str,
                           compiled_file_name: str = DEFAULT_COMPILED_FILE_NAME,
                           opt_flag: str = "O0",
                           number_of_runs: int = 3) -> float:
    """
    Compiles a source file with given flag choices
    and returns the benchmark time of the compiled code
    """

    compile_with_flags(opt_flag, compiled_file_name, source_code_file_name)
    return time_needed(number_of_runs, run_compiled_code)


def time_needed(number_of_repetitions: int, function_to_run: callable) -> float:
    """For measuring time for a function to run"""
    start = time()
    for j in range(0, number_of_repetitions):
        function_to_run()
    end = time()
    # time.time returns time in seconds, so conversion is not needed
    return (end - start) / number_of_repetitions


def run_compiled_code(compiled_code_file: str = DEFAULT_COMPILED_FILE_NAME) -> None:
    """ Executes the compiled code file """
    subprocess.run(f"./{compiled_code_file}", shell=True, cwd=os.getcwd())
