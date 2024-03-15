"""A Class to read domain-choice flags from a .json file"""
import json
from reader.flag_file_reader import FlagFileReader

class DomainFlagReader(FlagFileReader):
    """A Class to read domain-choice flags from a .json file"""

    all_names: list[str]
    domains: dict[str, str|list[str]]
    defaults: dict[str, str]
    def __init__(self, file_name: str):
        """:param file_name: The name of the file to read in from"""
        super().__init__(file_name)
        self.all_names = []
        self.domains = {}
        self.defaults = {}

    def read_in_flags(self) -> None:
        """Read the domain flags, their domains, and the default choices"""
        loaded_data = json.load(self.file)
        # Identify each name
        all_flags = loaded_data["flags"]
        self.all_names = [flag["flagname"] for flag in all_flags]

        for flag in all_flags:
            # Extract domains
            if flag["domaintype"] == "Choice":
                self.domains[flag["flagname"]] = flag["choices"]
            else:
                self.domains[flag["flagname"]] = flag["domaintype"]

        # Get default choices
        self.defaults = {flag["flagname"]: flag["default"] for flag in all_flags}

    def get_flags(self) -> list[str]:
        """Return a list of all the flag names"""
        return self.all_names

    def get_domains(self) -> dict[str, str|list[str]]:
        """Return a `dict` mapping the flag names to their corresponding domain"""
        return self.domains

    def get_default_values(self) -> dict[str, str]:
        """Return a `dict` mapping the default flag names to their corresponding default value"""
        return self.defaults
