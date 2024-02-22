""" A class containing the benchmarking info and behaviour"""
import signal
import sys
from itertools import islice, repeat
from multiprocessing.pool import Pool
from time import time
import subprocess
import os

DEFAULT_COMPILED_FILE_NAME = "filetotest"

class Benchmarker:
    """A class containing the benchmarking info and behaviour"""
    GLOBAL_COUNTER = 0

    def __init__(self, source_code_to_benchmark: str, compiled_file_name: str = DEFAULT_COMPILED_FILE_NAME):
        self.SOURCE_CODE_FILE = source_code_to_benchmark
        self.COMPILED_CODE_FILE = compiled_file_name

    def compile_with_flags(self,
                           output_file_name: str,
                           opt_flag: str = "O0") -> str:
        """Compile a c++ source code file with the specified flags"""
        subprocess.run(
            [f"g++ {opt_flag} -w -o {output_file_name} {self.SOURCE_CODE_FILE}"],
            shell=True, cwd=os.getcwd())
        return output_file_name


    def benchmark_flag_choices(self,
                               opt_flag: str = "-O0",
                               number_of_runs: int = 3) -> float:
        """
        Compiles a source file with given flag choices
        and returns the benchmark time of the compiled code
        """
        # new_name = self.generate_unique_outputfile_names(0, number_of_runs-1)
        self.compile_with_flags(self.COMPILED_CODE_FILE, opt_flag)
        return self.time_needed(number_of_runs, self.run_compiled_code, self.COMPILED_CODE_FILE)

    @staticmethod
    def time_needed(number_of_repetitions: int,
                    function_to_run: callable,
                    output_file_name: str) -> float:
        """For measuring time for a function to run"""
        for j in range(number_of_repetitions):
            start = time()
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

    @staticmethod
    def generate_unique_outputfile_names(start: int, end: int):
        for i in range(start, end):
            yield ''.join([DEFAULT_COMPILED_FILE_NAME, str(i+1)])

    #TODO: Base this on the number of cores in a machine
    def parallel_benchmark_flags(self, flag_string_to_benchmark: str, n_runs: int) -> float:
        output_names = list(islice(self.generate_unique_outputfile_names(0, n_runs), n_runs))
        with Pool(n_runs) as pool:
            # Compile each file with a unique output file name
            output_names = pool.starmap(self.compile_with_flags,
                                        zip(output_names,
                                            repeat(flag_string_to_benchmark, n_runs)))
            # Create the list of arguments to pass to self.time_needed
            args_list = zip(list(repeat(1, n_runs)),
                            list(repeat(self.run_compiled_code, n_runs)),
                            output_names)
            # Run and benchmark the compiled files in parallel
            times = pool.starmap(self.time_needed, args_list)
        for name in output_names:
            os.remove(name)

        return sum(times)/n_runs
