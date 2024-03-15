"""A module with miscellaneous helper methods"""

from random import getrandbits, choice, randint
from typing import Any

from core.flags import Flags
from helpers.constants import INTEGER_DOMAIN_UPPER_BOUND

def get_random_integer(lower_bound = 1, upper_bound = INTEGER_DOMAIN_UPPER_BOUND) -> int:
    """
    Get a random integer value

    :param lower_bound: The lower bound (inclusive) of the integers to randomly choose from
    :param upper_bound: The upper bound (inclusive) of the integers to randomly choose from
    :return: A random integer from the provided range
    """
    return randint(lower_bound, upper_bound)

def get_random_flag_sample(flags: Flags) -> dict[str, bool|str]:
    """
    Get a random sample from a set of flags

    :param flags: A `Flags` object containing the flags to randomly choose from
    :return: A dictionary of flag names, mapped to their randomly chosen values
    """
    flag_choices = {}
    for flag_name in flags.get_all_flag_names():
        flag_choices[flag_name] = get_random_individual_flag_choice(flags, flag_name)
    return flag_choices

def get_random_individual_flag_choice(flags_obj: Flags, flag_name: str) -> str|bool|int:
    """
    Get a random choice for a given flag

    :param flags_obj: A `Flags` object containing the given flag
    :param flag_name: The name of the flag to obtain a random value for
    :return: A randomly chosen value from the given flag's domain
    """
    domain = flags_obj.get_flag_domain(flag_name)
    match domain:
        case "Integer":
            return get_random_integer()
        case "Integer-or-binary":
            use_integer = bool(getrandbits(1))
            if use_integer:
                return get_random_integer()
            else:
                return bool(getrandbits(1))
        case "Integer-align":
            # For now - just use a random integer
            return get_random_integer()
        case [*domain_values]:
            # Special case for live-patching
            if flag_name == "-flive-patching":
                domain_values += [False]
                return choice(domain_values)
            return choice(domain_values)
        case _:
            raise ValueError(f"Unrecognised flag domain {domain} for flag {flag_name}")

def create_flag_string(flag_choices: dict[str, bool|str]) -> str:
    """
    Creates a string of compiler flags that can be used to run the compiler

    :param flag_choices: The flags to be/not be used by the compiler
    :return: A string of compiler flags in the format to run the compilation
    """
    final_str = ""
    for flag_name, flag_choice in flag_choices.items():
        # Binary flags
        if type(flag_choice) == bool:
            if flag_choice:
                final_str += f"{flag_name} "
            else:
                # Case where the flag is not chosen
                if flag_name == "-flive-patching":
                    # In this case, the flag has no option to turn it off explicitly - it just needs to be omitted
                    pass
                else:
                    final_str += f"{flag_name.replace("-f", "-fno-", 1)} "

        # Non-binary/domain flags
        else:
            if type(flag_choice) == int:
                final_str += f"{flag_name}={str(flag_choices[flag_name])} "
            else:
                final_str += f"{flag_name}={flag_choices[flag_name]} "


    return final_str
