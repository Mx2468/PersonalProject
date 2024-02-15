"""
A file with miscellaneous helper methods
Currently only a flag string helper method
"""

from random import getrandbits

def get_random_flag_sample(flags: list[str]) -> dict[str, bool]:
    """
    Get a random sample from a set of binary flags
    :param flags: A list of binary flags
    :return: A dictionary of flags, along with if they were chosen or not
    """
    return {flag: bool(getrandbits(1)) for flag in flags}


def create_flag_string(flag_choices: dict[str, bool]) -> str:
    """
    Creates a string of compiler flags that can be used to run the compiler

    :param flag_choices: The flags to be/not be used by the compiler

    :return: A string of compiler flags in the format to run the compilation
    """

    final_str = ""
    for flag_name, choice in flag_choices.items():
        if choice:
            final_str += f"{flag_name} "
        else:
            # Case where the flag is not chosen
            final_str += f"{flag_name.replace("-f", "-fno-", 1)} "

    return final_str
