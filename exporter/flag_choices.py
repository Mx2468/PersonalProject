from core.flags import Flags

class FlagChoicesExporter:
    def __init__(self, file_name: str, flags: dict[str, bool|str]):
        """
        :param file_name: A path for the file to write to
        """
        self.file = None
        self.file_name = file_name
        self.flags = flags

    def __enter__(self) -> 'FlagFileReader':
        """Overwrites magic method to allow easy use with "with" statements"""
        self.file = open(self.file_name, 'w', encoding='UTF-8')
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        """Uses magic method to close the file after we're done with it in a "with" statement"""
        self.file.close()

    def export_flags(self):
        print(f"Writing flag choices to {self.file_name}")
        for flag_name, value in self.flags.items():
            self.file.write(f"{flag_name}={value} ")