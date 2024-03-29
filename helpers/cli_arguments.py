"""A module to handle the definition of CLI arguments."""
import argparse
import helpers.constants as constants

def get_cli_arguments() -> argparse.Namespace:
    """
    Defines, parses and returns the program's CLI arguments/flags

    :return: An `argparse.Namespace` object containing the parsed CLI arguments and their provided values
    """
    argparser = argparse.ArgumentParser(prog="Compiler flag optimiser",
                            description="A piece of software to optimise the optimisation options for the g++ compiler, given an input c++ file.")

    argparser.add_argument("-i", "--input",
                           dest="input",
                           help="Path to the input c++ file to optimise flag choices for.")

    argparser.add_argument("-bf", "--binary-flags",
                           dest="b_input_flags",
                           help="Paths to the binary (true/false) input flags as a .txt file.",
                           default=constants.ALL_BINARY_FLAGS_PATH)

    argparser.add_argument("-df", "--domain-flags",
                           dest="d_input_flags",
                           help="Path to the domain flags file (.json format).",
                           default=constants.ALL_DOMAIN_FLAGS_PATH)

    argparser.add_argument("-o", "--output",
                           dest="output",
                           help="Path to the output file to write the flag choices to.",
                           default="flags_dump.txt")

    argparser.add_argument("-m", "--method",
                           dest="method",
                           help="Optimisation method used to optimise the flag choices.",
                           choices=["random", "genetic", "gaussian"],
                           default="random")

    argparser.add_argument("-n", "--opt-steps",
                           dest="opt_steps",
                           help="Number of optimisation steps to run. No value or a value below 1 means an anytime-algorithm will run.",
                           default=-1)

    argparser.add_argument("--num-code-runs",
                           dest="n_code_runs",
                           help="Number of code runs used to benchmark the ")

    argparser.add_argument("--dont-start-with-o3",
                           dest="dont_start_o3",
                           action='store_true',
                           help="Do not start with 03 flags as a base.")

    argparser.add_argument("--dont-compare-with-o3",
                           dest="dont_compare_o3",
                           action='store_true',
                           help="Skip comparing with 03 flags after the optimisation of the flag choices has finished.")

    argparser.add_argument("--dont-use-standard-breaking-flags",
                           dest="dont_use_standard_breaking_flags",
                           action='store_true',
                           help="Skip using optimisation flags that break the C++ standard")

    return argparser.parse_args()