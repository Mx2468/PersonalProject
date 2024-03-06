"""A Module to run and control the running of the flag optimisation"""
import os
import sys

from optimisers import *
import signal
from helpers import constants, Benchmarker
from multiprocessing import Manager

def init_globals(flag, lock):
    global global_flag
    global global_lock
    global_flag = flag
    global_lock = lock

# Instance of Exception with a readable name to handle returning to
class ReturnToMain(Exception):
    pass

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

    def contract_optimisation(self,
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
        return optimiser.fastest_flags

    def anytime_optimisation(self,
                             optimiser: FlagOptimiser,
                             benchmark_obj: Benchmarker) -> dict[str, bool|str]:
        """
        Runs the optimisation loop until the computation is stopped via ctrl+c,
        then prints out the flags to the user
        :param optimiser: The optimiser object that will be used to optimise the flags
        :param benchmark_obj: The object for benchmarking
        :return The dictionary of flags and whether they were chosen or not
        """
        def return_results(*args) -> None:
            # Global value used between threads to make sure this message is only printed once
            # (i.e. by only one thread)
            with global_lock:
                if global_flag.value == 0:
                    global_flag.value = 1
                    print('You pressed ^C!')
                    print(f"States Explored: {optimiser.states_explored}")
                    print(f"Fastest Time: {optimiser.fastest_time}s")
                    print(f"Fastest Flags: {create_flag_string(optimiser.fastest_flags)}")
                    raise ReturnToMain

        try:
            signal.signal(signal.SIGINT, return_results)

            # Manager object used to coordinate shared value and lock across objects - ensures end result is only printed once
            with Manager() as manager:
                # Create shared Value & Lock
                shared_flag = manager.Value('i', 0)
                shared_lock = manager.Lock()

                # Initialise globals for each process
                init_globals(shared_flag, shared_lock)
                return optimiser.continuous_optimise(benchmark_obj)

        except KeyboardInterrupt:
            print("Interrupted")

        except ReturnToMain:
            return optimiser.get_fastest_flags()


    def dump_flags(self, filename: str, flags: dict[str, bool|str]) -> None:
        with open(filename, 'w') as file_obj:
            for flag_name, value in flags.items():
                file_obj.write(f"{flag_name}={value}\n")

#TODO have cli flags control which optimisation method and approach to use (default random search anytime algorithm)
#TODO: Implement dumping of the flags to a file or stdout at the end of anytime optimisation
#TODO: Change as many class attributes as possible to private
if __name__ == '__main__':
    SOURCE_CODE_FILE = os.path.join(constants.SOURCE_CODE_DIR, "BreadthFSSudoku.cpp")
    controller = FlagOptimisationController("flags/binary_flags.txt",
                                            "flags/domain_flags.json",
                                            SOURCE_CODE_FILE)

    benchmarker = Benchmarker(SOURCE_CODE_FILE)


    o3_flags_obj = Flags()
    o3_flags_obj.load_in_flags("./flags/O3_flags.txt", "./flags/domain_flags.json")

    # TODO: Implement a reader to load these flags in as true/their default values as provided to allow them to be used directly
    o3_flags = {bin_flag: True for bin_flag in o3_flags_obj.get_all_flag_names()}
    for domain_flag, value in o3_flags_obj.get_domain_flag_defaults().items():
        o3_flags[domain_flag] = value
    for flag in controller.flags.get_all_flag_names():
        if not (flag in o3_flags.keys()):
            o3_flags[flag] = False

    o3_flags = validate_flag_choices(o3_flags)
    # print(f"o3_flags: {o3_flags}")
    # sys.exit(0)

    optimiser = GeneticAlgorithmOptimiser(controller.flags, 4, [o3_flags])
    controller.anytime_optimisation(optimiser, benchmarker)
    benchmarker.compare_with_o3(create_flag_string(optimiser.get_fastest_flags()))
