""" A class containing the benchmarking info and behaviour"""

from time import time
import subprocess
import os

DEFAULT_COMPILED_FILE_NAME = "filetotest"


class Benchmarker:
    """A class containing the benchmarking info and behaviour"""

    # Counter to create distinct file names
    GLOBAL_COUNTER = 1

    def __init__(self, source_code_to_benchmark: str, compiled_file_name: str = DEFAULT_COMPILED_FILE_NAME):
        self.SOURCE_CODE_FILE = source_code_to_benchmark
        self.COMPILED_CODE_FILE = compiled_file_name

    def compile_with_flags(self,
                           output_file_name: str,
                           opt_flag: str = "O0"):
        """Compile a c++ source code file with the specified flags"""
        subprocess.run(
            [f"g++ {opt_flag} -w -o {output_file_name} {self.SOURCE_CODE_FILE}"],
            shell=True, cwd=os.getcwd())


    def benchmark_flag_choices(self,
                               opt_flag: str = "-O0",
                               number_of_runs: int = 3) -> float:
        """
        Compiles a source file with given flag choices
        and returns the benchmark time of the compiled code
        """
        new_name = self.get_fresh_file_name()
        self.compile_with_flags(new_name, opt_flag)
        return self.time_needed(number_of_runs, self.run_compiled_code, new_name)

    @staticmethod
    def time_needed(number_of_repetitions: int,
                    function_to_run: callable,
                    output_file_name: str) -> float:
        """For measuring time for a function to run"""
        start = time()
        for j in range(0, number_of_repetitions):
            function_to_run(output_file_name)
        end = time()
        # time.time returns time in seconds, so conversion is not needed
        return (end - start) / number_of_repetitions


    def run_compiled_code(self, *args) -> None:
        """Executes the compiled code file """
        subprocess.run(f"./{args[0]}", shell=True, cwd=os.getcwd())

    def get_fresh_file_name(self) -> str:
        name = self.COMPILED_CODE_FILE + str(self.GLOBAL_COUNTER)
        self.GLOBAL_COUNTER += 1
        return name

    def compare_with_o3(self, opt_flag: str) -> None:
        """Benchmarks the flags against the -O3 "golden standard" and returns the better one"""
        flags_time = self.benchmark_flag_choices(opt_flag)
        o3_time = self.benchmark_flag_choices("-O3")
        print(f"Fastest flags time: {flags_time}")
        print(f"O3 time: {o3_time}")
        if flags_time < o3_time:
            print("These flags are better than O3!")
        else:
            print("These flags perform just as well or worse than O3")