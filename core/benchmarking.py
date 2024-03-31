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
        """
        :param source_code_to_benchmark: The source code file to use for benchmarking flag choices
        :param compiled_file_name: The name of the compiled binary file to use
        (this defaults to "filetotest", but can be specified depending on the user's environment)
        """

        self.SOURCE_CODE_FILE = source_code_to_benchmark
        self.COMPILED_CODE_FILE = compiled_file_name

    def compile_with_flags(self,
                           output_file_name: str,
                           opt_flag: str) -> str:
        """
        Compile a c++ source code file with the specified flags

        :param output_file_name: The name of the compiled executable file at the end of the compilation process
        :param opt_flag: The string of optimisation flags to use for the compilation process
        :returns: The name of the compiled file name as a string
        """
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
        Compiles a source file with given flag choices iteratively for a number of runs
        and returns the benchmark time of the compiled code.

        :param opt_flag: The string of optimisation flags to use for the benchmarking
        :param number_of_runs: The number of runs over which to average the compilation process
        :returns: The average time taken to run the compiled code
        """
        compiled_code_name = self.compile_with_flags(self.COMPILED_CODE_FILE, opt_flag)
        return self.time_needed(number_of_runs, self.run_compiled_code, compiled_code_name)

    @staticmethod
    def time_needed(number_of_repetitions: int,
                    function_to_run: callable,
                    output_file_name: str) -> float:
        """
        General function for measuring the time taken for a function to run over a number of repetitions

        :param number_of_repetitions: The number of runs over which the runtime is averaged
        :param function_to_run: The function that runs the code (self.run_compiled_code)
        :param output_file_name: The name of the compiled executable file
        :returns: The average time taken for the function to run over the number of repetitions provided
        """
        for j in range(number_of_repetitions):
            start = time()
            function_to_run(output_file_name)
            end = time()
        # time.time returns time in seconds, so conversion is not needed
        return (end - start) / number_of_repetitions


    def run_compiled_code(self, *args) -> None:
        """
        Executes the compiled code file, where the first argument in *args
        should be the name of the compiled executable file to run

        :param args: The to be provided to the run function (There should only be one argument,
        and that is the string name of the compiled code file)
        """
        # DEVNULL used to supress stdout - removes unnecessary prints
        # clogging up the console and obstructing optimisation information
        subprocess.run(f"./{args[0]}", shell=True, cwd=os.getcwd(), stdout=subprocess.DEVNULL)

    def get_fresh_file_name(self) -> str:
        """
        Returns a unique name for the compiled executable file to run

        :return: The name of the compiled executable as a string
        """
        name = self.COMPILED_CODE_FILE + str(self.GLOBAL_COUNTER)
        self.GLOBAL_COUNTER += 1
        return name

    def compare_with_o3(self, optimised_flags: str, o3_flags: str) -> float:
        """
        Benchmarks and compares a given set of flag choices with -O3 flags.

        :param optimised_flags: A string of the optimised flags
        :param o3_flags: A string representing the flags used in -O3
        :returns: The percentage change between the two flag choices
        """

        opt_flag_time = self.parallel_benchmark_flags(optimised_flags)
        o3_flag_time = self.parallel_benchmark_flags(o3_flags)

        print(f"\nOptimised flag time {opt_flag_time}")
        print(f"O3 flag time {o3_flag_time}")

        if opt_flag_time < o3_flag_time:
            print("The optimised flags are faster than -O3")
        else:
            print("The optimised flags perform the same or worse than -O3")
        percentage_change = ((o3_flag_time-opt_flag_time)/o3_flag_time)*100
        return percentage_change

    def compare_two_flag_choices(self, opt_flag1: str, reference_flags: str ) -> float:
        """
        A function to compare two different strings of flag choices

        :param opt_flag1: The first set of flag choices
        :param opt_flag2: The second set of flag choices
        :returns: The percentage change between the two flag choices
        """
        flags_time1 = self.parallel_benchmark_flags(opt_flag1)
        flags_time2 = self.parallel_benchmark_flags(reference_flags)

        print(f"\nOptimised flag time: {flags_time1}")
        print(f"Reference flag time: {reference_flags}")

        if flags_time1 < flags_time2:
            print("The optimised flags are faster than the reference")
        else:
            print("The optimised flags perform the same or worse than the reference")
        percentage_change = ((flags_time2 - flags_time1) / flags_time2) * 100
        return percentage_change

    @staticmethod
    def generate_unique_outputfile_names(start: int, end: int):
        """
        Generates a set of unique output file names for multiple threads

        :param start: The beginning number of the range of numbers to use in the file names
        :param end: The end number of the range of numbers to use in the file names
        :return: A generator of unique file names, using the range provided
        """
        for i in range(start, end):
            yield ''.join([DEFAULT_COMPILED_FILE_NAME, str(i+1)])

    def parallel_benchmark_flags(self, flag_string_to_benchmark: str, n_runs: int = N_BENCHMARK_RUNS) -> float:
        """
        Run and benchmark a flag string in parallel

        :param flag_string_to_benchmark: The string of optimisation flags to benchmark
        :param n_runs: The number of benchmark runs to run in parallel and average the result over
        :return: The averaged time taken to run the program with the given flags
        """
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
