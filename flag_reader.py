# Module to read in flags for the compiler to use
from os import read

def read_binary_flags() -> list[str]:
    """Read binary flags from the known location"""
    with open("binary_flags.txt", "r") as flagfile:
        flags = [line.strip() for line in flagfile]
        return flags
