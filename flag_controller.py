"""A Module to run and control the running of the flag optimisation"""
import os
import sys

from helpers.cli_arguments import get_cli_arguments
from optimisers import *
import signal
from helpers import constants
from core.benchmarking import Benchmarker
from multiprocessing import Manager

# Sets up global variables for lock and value for processess to commuinicate
def init_globals(flag, lock):
    global global_flag
    global global_lock
    global_flag = flag
    global_lock = lock

#TODO: Export this into another module for modularity
def dump_flags(filename: str, flags: dict[str, bool|str]) -> None:
    print(f"Writing flag choices to {filename}")

    with open(filename, 'w') as file_obj:
        for flag_name, value in flags.items():
            file_obj.write(f"{flag_name}={value} ")


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
                 compiled_code_name: str = constants.COMPILED_CODE_FILE,
                 **kwargs):
        """
        :param binary_flags_file: The path to the file containing the binary choice flags
        :param domain_flags_file: The path to the file containing the domain choice flags
        :param source_code_file: The path to the source code to be compiled
        :param compiled_code_name: A path/name for the intermediate compiled executable file
        (not necessary for most uses - only if the environment rejects the default name)
        """
        self.SOURCE_CODE_FILE = source_code_file
        self.COMPILED_CODE_FILE = compiled_code_name

        flags_obj = Flags()
        flags_obj.load_in_flags(binary_flags_file, domain_flags_file)
        if dont_use_standard_breaking_flags:
           print("Turning off standard-breaking flags")
           for flag_name in ["-ffast-math", "-fallow-store-data-races"]:
               flags_obj.remove_flag(flag_name)
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
        print(f"Running optimisation for {n_steps} steps")
        optimiser.n_steps_optimise(benchmark_obj, n_steps)
        print('The optimisation process finished')
        print(f"States Explored: {optimiser.states_explored}")
        print(f"Fastest Time: {optimiser.fastest_time}s")
        print(f"Fastest Flags: {create_flag_string(optimiser.fastest_flags)}")
        global output_file
        dump_flags(output_file, optimiser.fastest_flags)
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
                    global output_file
                    dump_flags(output_file, optimiser.fastest_flags)
                    raise ReturnToMain

        try:
            print("Using anytime algorithm for optimisation, press ^C to stop and return flags")
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
            pass

        except ReturnToMain:
            return optimiser.get_fastest_flags()

# TODO: Add run scripts for a variety of necessary scenarios
# TODO: Change as many class attributes as possible to private
if __name__ == '__main__':
    # Define all input arguments

    parsed_args = get_cli_arguments()

    # Read in all arguments
    input_source_code_file = str(parsed_args.input)
    output_file = parsed_args.output
    opt_method = parsed_args.method
    opt_steps = parsed_args.opt_steps
    binary_input_flags = str(parsed_args.b_input_flags)
    domain_input_flags = str(parsed_args.d_input_flags)
    dont_start_o3 = parsed_args.dont_start_o3
    dont_compare_o3 = parsed_args.dont_compare_o3
    dont_use_standard_breaking_flags = parsed_args.dont_use_standard_breaking_flags

    # Make sure input source code is a c++ file - checks some of the most common c++ file endings.
    assert input_source_code_file.endswith((".cpp", ".C", ".cc")), "The input file must be a valid c++ file"

    controller = FlagOptimisationController(binary_input_flags,
                                            domain_input_flags,
                                            input_source_code_file,
                                            dont_use_standard_breaking_flags=dont_use_standard_breaking_flags)

    benchmarker = Benchmarker(input_source_code_file)

    # TODO: Implement a reader to load these flags in as true/their default values as provided to allow them to be used directly
    o3_flags_obj = Flags()
    o3_flags_obj.load_in_flags("./flags/O3_flags.txt", "./flags/o3_domain_flags.json")
    all_flags = controller.flags.get_all_flag_names()
    o3_flag_names = o3_flags_obj.get_all_flag_names()
    for flag in all_flags:
        o3_flags_obj.add_flag(flag, controller.flags.get_flag_domain(flag),
                              controller.flags.get_flag_default(flag))

    o3_flags = {bin_flag: True for bin_flag in o3_flags_obj.get_all_flag_names()}
    for domain_flag, value in o3_flags_obj.get_domain_flag_defaults().items():
        o3_flags[domain_flag] = value

    # By itself, the flags combination for 03 mentioned in the GCC page causes errors - this needs to be validated
    o3_flags = validate_flag_choices(o3_flags)

    if dont_start_o3:
        flags_to_start = []
    else:
        flags_to_start = [o3_flags]

    if opt_method == "genetic":
        print("Using a genetic algorithm")
        optimiser = GeneticAlgorithmOptimiser(controller.flags, starting_population=flags_to_start)
    elif opt_method == "random":
        print("Using random search")
        optimiser = RandomSearchOptimiser(controller.flags)
    else:
        raise ValueError("Invalid optimization method provided, only 'genetic' and 'random' are supported ")

    if opt_steps is None or opt_steps <= 0:
        fastest_flags = controller.anytime_optimisation(optimiser, benchmarker)
    else:
        fastest_flags = controller.contract_optimisation(opt_steps, optimiser, benchmarker)

    if dont_compare_o3:
        pass
    else:
        print("\nPlease wait for your flags to be compared with that of -03")
        benchmarker.compare_with_o3(
            optimised_flags=create_flag_string(fastest_flags),
            o3_flags=create_flag_string(o3_flags))
        print("Press ^C again to exit")
    sys.exit(0)
