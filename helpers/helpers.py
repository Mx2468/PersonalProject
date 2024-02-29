"""
A file with miscellaneous helper methods
Currently only a flag string helper method
"""

from random import getrandbits, choice, randint

from core.flags import Flags
from helpers.constants import INTEGER_DOMAIN_UPPER_BOUND


def get_random_integer(lower_bound = 1, upper_bound = INTEGER_DOMAIN_UPPER_BOUND) -> int:
    return randint(lower_bound, upper_bound)

def get_random_flag_sample(flags: Flags) -> dict[str, bool|str]:
    """
    Get a random sample from a set of binary flags
    :param flags: A list of binary flags
    :return: A dictionary of flags, along with if they were chosen or not
    """
    flag_choices = {}
    for flag_name in flags.get_all_flag_names():
        domain = flags.get_flag_domain(flag_name)
        match domain:
            case "Integer":
                flag_choices[flag_name] = get_random_integer()
            case "Integer-or-binary":
                use_integer = bool(getrandbits(1))
                if use_integer:
                    flag_choices[flag_name] = get_random_integer()
                else:
                    flag_choices[flag_name] = bool(getrandbits(1))
            case "Integer-align":
                # For now - just use a random integer
                flag_choices[flag_name] = get_random_integer()
            case [*domain_values]:
                flag_choices[flag_name] = choice(domain_values)
            case _ :
                raise ValueError(f"Unrecognised flag domain {domain} for flag {flag_name}")

    return flag_choices


def create_flag_string(flag_choices: dict[str, bool|str]) -> str:
    """
    Creates a string of compiler flags that can be used to run the compiler

    :param flag_choices: The flags to be/not be used by the compiler

    :return: A string of compiler flags in the format to run the compilation
    """
    final_str = ""
    for flag_name, flag_choice in flag_choices.items():
        if flag_choice == True or flag_choice == False:
            if flag_choice:
                final_str += f"{flag_name} "
            else:
                # Case where the flag is not chosen
                final_str += f"{flag_name.replace("-f", "-fno-", 1)} "
        else:
            final_str += f"{flag_name}={flag_choices[flag_name]} "

    return final_str
