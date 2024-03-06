"""A Module to run and control the running of the flag optimisation"""
import os
import sys

from optimisers import *
import signal
from helpers import constants, Benchmarker
from multiprocessing import Manager

import argparse

def init_globals(flag, lock):
    global global_flag
    global global_lock
    global_flag = flag
    global_lock = lock

def dump_flags(filename: str, flags: dict[str, bool|str]) -> None:
    with open(filename, 'w') as file_obj:
        for flag_name, value in flags.items():
            file_obj.write(f"{flag_name}={value}\n")


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
        dump_flags("flag_dump.txt", optimiser.fastest_flags)
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
                    dump_flags("flag_dump.txt", optimiser.fastest_flags)
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


#TODO: Change as many class attributes as possible to private
if __name__ == '__main__':
    argparser = argparse.ArgumentParser(prog="Compiler flag optimiser",
                            description="A piece of software to optimise the optimisation options for the g++ compiler, given an input c++ file.")

    argparser.add_argument("-i", "--input",
                           dest="input",
                           help="Path to the input c++ file to optimise flag choices for.")

    argparser.add_argument("-bf", "--binary-flags",
                           dest="b_input_flags",
                           help="Paths to the binary (true/false) input flags as a .txt file.",
                           default="flags/binary_flags.txt")

    argparser.add_argument("-df", "--domain-flags",
                           dest="d_input_flags",
                           help="Path to the domain flags file (.json format).",
                           default="flags/domain_flags.json")

    argparser.add_argument("-o", "--output",
                           dest="output",
                           help="Path to the output file to write the flag choices to.")

    argparser.add_argument("-m", "--method",
                           dest="method",
                           help="Optimisation method used to optimise the flag choices.",
                           choices=["random", "genetic"],
                           default="genetic")

    argparser.add_argument("-n", "--opt-steps",
                           dest="opt_steps",
                           help="Number of optimisation steps to run. No value or a value below 1 means an anytime-algorithm will run.")

    argparser.add_argument("--start-with-o3",
                           dest="start_o3",
                           choices=["true", "false"],
                           action='store_true')

    argparser.add_argument("--compare-with-o3",
                           dest="compare_o3",
                           choices=["true", "false"],
                           action='store_true',
                           help="Compare with 03 flags after the optimisation of the ")

    parsed_args = argparser.parse_args()

    input_source_code_file = parsed_args.input
    output_file = parsed_args.output
    opt_method = parsed_args.method
    opt_steps = parsed_args.opt_steps
    binary_input_flags = parsed_args.b_input_flags
    domain_input_flags = parsed_args.d_input_flags

    controller = FlagOptimisationController(binary_input_flags,
                                            domain_input_flags,
                                            input_source_code_file)

    benchmarker = Benchmarker(input_source_code_file)


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

    optimiser = GeneticAlgorithmOptimiser(controller.flags, 10, [o3_flags])

    if opt_steps is None or opt_steps <= 0:
        fastest_flags = controller.anytime_optimisation(optimiser, benchmarker)
    else:
        fastest_flags = controller.contract_optimisation(opt_steps, optimiser, benchmarker)

    benchmarker.compare_two_flag_choices(
        opt_flag1=create_flag_string(fastest_flags),
        opt_flag2=create_flag_string(o3_flags))
    sys.exit(0)
