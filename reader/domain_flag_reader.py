import json
from reader.flag_file_reader import FlagFileReader

class DomainFlagReader(FlagFileReader):
    def __init__(self, file_name: str):
        super().__init__(file_name)

    def read_in_flags(self) -> None:
        """Read domain flags"""
        print(json.load(self.file))
        # Identify each name
        # Extract domains
        # combine both into flags info self.flags