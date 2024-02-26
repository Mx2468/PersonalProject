from reader import binary_flag_reader, domain_flag_reader


class FlagChoices:
    all_flag_names: list[str]
    binary_flag_choices: dict[str, bool]
    flag_domains: dict[str, str]
    domain_flag_choices: dict[str, str]

    def __init__(self, flags: list[str]):
        self.all_flag_names = []
        self.binary_flag_choices = {flag: False for flag in flags}

    def load_in_flags(self, binary_flag_path: str, domain_flag_path: str):
        with binary_flag_reader.BinaryFlagReader(binary_flag_path) as bin_flags_reader:
            bin_flags_reader.read_in_flags()
            self.all_flag_names += bin_flags_reader.get_flags()

        with domain_flag_reader.DomainFlagReader(domain_flag_path) as domain_reader:
            domain_reader.read_in_flags()
            self.all_flag_names += domain_reader.get_flags()
            self.domain_flag_choices = domain_reader.get_default_values()

    def get_binary_flag_choices(self) -> dict[str, bool]:
        return self.binary_flag_choices

    def get_all_flag_names(self) -> list[str]:
        return self.all_flag_names

    def get_domain_flag_choices(self) -> dict[str, str]:
        return self.domain_flag_choices
