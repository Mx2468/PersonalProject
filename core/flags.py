from reader import binary_flag_reader, domain_flag_reader

class Flags:
    all_flag_names: list[str]
    flag_domains: dict[str, str|list[str]|list[bool]]
    domain_flag_defaults: dict[str, str]

    def __init__(self):
        pass

    def load_in_flags(self, binary_flag_path: str, domain_flag_path: str) -> None:
        """
        Loads in the flag info from the binary and domain flag paths provided
        :param binary_flag_path: The path for information about the binary flags (a .txt file)
        :param domain_flag_path: The path for information about the domain flags (a .json file)
        """
        with binary_flag_reader.BinaryFlagReader(binary_flag_path) as bin_flags_reader:
            bin_flags_reader.read_in_flags()
            self.all_flag_names += bin_flags_reader.get_flags()
            for flag_name in self.all_flag_names:
                self.flag_domains[flag_name] = [True, False]

        with domain_flag_reader.DomainFlagReader(domain_flag_path) as domain_reader:
            domain_reader.read_in_flags()
            self.all_flag_names += domain_reader.get_flags()
            self.domain_flag_defaults= domain_reader.get_default_values()

    def get_all_flag_names(self) -> list[str]:
        """Returns a list of all the flag names"""
        return self.all_flag_names

    def get_domain_flag_defaults(self) -> dict[str, str]:
        """Returns a dictionary mapping each flag name to its default value"""
        return self.domain_flag_defaults

    def get_all_flag_domains(self) -> dict[str, str|list[str]|list[bool]]:
        """Returns a dictionary mapping all flag names to the domains that can be applied to them"""
        return self.flag_domains

    def get_flag_domain(self, flag_name: str) -> str|list[str]|list[bool]:
        """Returns a domain given a specific flag name"""
        return self.flag_domains[flag_name]
