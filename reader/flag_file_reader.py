"""An abstract class of readers for flag files"""
from abc import ABC, abstractmethod
class FlagFileReader(ABC):
    """An abstract class of readers for flag files"""
    def __init__(self, file_name: str):
        """
        :param file_name: A path for the file to read in
        """
        self.file = None
        self.file_name = file_name

    def __enter__(self) -> None:
        """Overwrites magic method to allow easy use with "with" statements"""
        self.file = open(self.file_name, 'r', encoding='UTF-8')

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        """Uses magic method to close the file after we're done with it in a "with" statement"""
        self.file.close()

    @abstractmethod
    def read_in_flags(self) -> list[str]:
        """
        Reads flags from the opened file and returns the read flags as a list

        :return: List of strings containing the read flags
        """
        raise NotImplementedError