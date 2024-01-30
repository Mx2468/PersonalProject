# Module to read in binary choice flags to optimise
from os import read
from reader.flag_file_reader import FlagFileReader

class BinaryFlagReader(FlagFileReader):
    """
    Reads binary (yes/no) flag choices from a .txt file,
    with each flag on a new line in the affirmative form
    (-f[flag] form as opposed to -fno[flag] form)
    """
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def read_in_flags(self) -> list[str]:
        """Read binary flags from the known location"""
        with open("../binary_flags.txt", "r") as flagfile:
            # Simple libe-by-line reading
            flags = [line.strip() for line in flagfile]
            return flags
