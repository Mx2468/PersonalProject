import json
from reader.flag_file_reader import FlagFileReader

class DomainFlagReader(FlagFileReader):
    all_names: list[str]
    domains: dict[str, str]
    defaults: dict[str, str]
    def __init__(self, file_name: str):
        super().__init__(file_name)

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
        return self.all_names

    def get_domains(self) -> dict[str, str]:
        return self.domains

    def get_default_values(self) -> dict[str, str]:
        return self.defaults
