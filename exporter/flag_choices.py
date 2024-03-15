"""A class to write out a choice of flags to a .txt file"""
import helpers

class FlagChoicesExporter:
    def __init__(self, file_name: str, flags: dict[str, bool|str]):
        """
        :param file_name: A path for the file to write to
        :param flags: A dictionary mapping flag names to their chosen values
        """
        self._file = None
        self._file_name = file_name
        self._flags = flags

    def __enter__(self) -> 'FlagFileReader':
        """Overwrites magic method to allow easy use with "with" statements"""
        self._file = open(self._file_name, 'w', encoding='UTF-8')
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        """Uses magic method to close the file after we're done with it in a "with" statement"""
        self._file.close()

    def export_flags(self) -> None:
        """Exports the provided flags to the filename provided"""
        print(f"Writing flag choices to {self._file_name}")
        self._file.write(helpers.create_flag_string(self._flags))