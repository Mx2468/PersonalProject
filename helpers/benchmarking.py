""" A class containing the benchmarking info and behaviour"""
from itertools import islice, repeat
from multiprocessing.pool import Pool
from time import time
import subprocess
import os

from helpers.constants import N_BENCHMARK_RUNS

DEFAULT_COMPILED_FILE_NAME = "filetotest"

class Benchmarker:
    """A class containing the benchmarking info and behaviour"""
    GLOBAL_COUNTER = 0

    def __init__(self,
                 source_code_to_benchmark: str,
                 compiled_file_name: str = DEFAULT_COMPILED_FILE_NAME):

        self.SOURCE_CODE_FILE = source_code_to_benchmark
        self.COMPILED_CODE_FILE = compiled_file_name

    def compile_with_flags(self,
                           output_file_name: str,
                           opt_flag: str) -> str:
        """Compile a c++ source code file with the specified flags"""
        if os.path.exists(output_file_name):
            os.remove(output_file_name)

        subprocess.run(
            [f"g++ {opt_flag} -w -fpermissive -o {output_file_name} {self.SOURCE_CODE_FILE}"],
            shell=True, cwd=os.getcwd())
        return output_file_name


    def benchmark_flag_choices(self,
                               opt_flag: str,
                               number_of_runs: int = N_BENCHMARK_RUNS) -> float:
        """
        Compiles a source file with given flag choices
        and returns the benchmark time of the compiled code
        """
        compiled_code_name = self.compile_with_flags(self.COMPILED_CODE_FILE, opt_flag)
        return self.time_needed(number_of_runs, self.run_compiled_code, compiled_code_name)

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
        subprocess.run(f"./{args[0]}", shell=True, cwd=os.getcwd(), stdout=subprocess.DEVNULL)

    def get_fresh_file_name(self) -> str:
        name = self.COMPILED_CODE_FILE + str(self.GLOBAL_COUNTER)
        self.GLOBAL_COUNTER += 1
        return name

    def compare_with_o3(self, optimised_flags: str, o3_flags: str) -> None:
        opt_flag_time = self.parallel_benchmark_flags(optimised_flags)
        o3_flag_time = self.parallel_benchmark_flags(o3_flags)

        if opt_flag_time < o3_flag_time:
            print("The optimised flags are faster than -O3")
        else:
            print("The optimised flags perform the same or worse than -O3")

    def compare_two_flag_choices(self, opt_flag1: str, opt_flag2: str ) -> None:
        flags_time1 = self.parallel_benchmark_flags(opt_flag1)
        flags_time2 = self.parallel_benchmark_flags(opt_flag2)
        print(f"Flags time 1: {flags_time1}")
        print(f"Flags time 2: {flags_time2}")

    @staticmethod
    def generate_unique_outputfile_names(start: int, end: int):
        for i in range(start, end):
            yield ''.join([DEFAULT_COMPILED_FILE_NAME, str(i+1)])

    #TODO: Base this on the number of cores in a machine
    def parallel_benchmark_flags(self, flag_string_to_benchmark: str, n_runs: int = N_BENCHMARK_RUNS) -> float:
        # Try-except statement used to prevent all current threads from printing the interrupt handling message
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
            try:
                os.remove(name)
            except FileNotFoundError:
                pass

        return sum(times)/n_runs
