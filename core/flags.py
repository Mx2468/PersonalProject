from reader import binary_flag_reader, domain_flag_reader

class Flags:
    all_flag_names: list[str]
    flag_domains: dict[str, str|list[str]|list[bool]]
    domain_flag_default: dict[str, str|bool]

    def __init__(self):
        self.all_flag_names = []
        self.flag_domains = {}
        self.domain_flag_default = {}

    def load_in_flags(self, binary_flag_path: str, domain_flag_path: str) -> None:
        """
        Loads in the flag info from the binary and domain flag paths provided
        :param binary_flag_path: The path for information about the binary flags (a .txt file)
        :param domain_flag_path: The path for information about the domain flags (a .json file)
        """
        # Get names and set domains/defaults of binary flags
        with binary_flag_reader.BinaryFlagReader(binary_flag_path) as bin_flags_reader:
            bin_flags_reader.read_in_flags()
            self.all_flag_names += bin_flags_reader.get_flags()
            for flag_name in self.all_flag_names:
                self.flag_domains[flag_name] = [True, False]
                # Automatically set flags to false - a "blank slate" being the default
                self.domain_flag_default[flag_name] = False

        # Get names and default values of the domain flags
        with domain_flag_reader.DomainFlagReader(domain_flag_path) as domain_reader:
            domain_reader.read_in_flags()
            self.all_flag_names += domain_reader.get_flags()
            self.domain_flag_default.update(domain_reader.get_default_values())

        # Get and assign domains of domain flags
        flag_domain_mapping = domain_reader.get_domains()
        for flag_name, domain in flag_domain_mapping.items():
          self.flag_domains[flag_name] = domain

    def remove_flag(self, flag_name: str) -> None:
        """ Remove a flag from the object"""
        if flag_name in self.all_flag_names:
            self.all_flag_names.remove(flag_name)
            if flag_name in self.flag_domains.keys():
                del self.flag_domains[flag_name]
                del self.domain_flag_default[flag_name]

    def add_flag(self, flag_name: str, domain, default_value) -> None:
        if not(flag_name in self.all_flag_names):
            self.all_flag_names.append(flag_name)

        if not(flag_name in self.flag_domains.keys()):
            self.flag_domains[flag_name] = domain

        if not(flag_name in self.domain_flag_default.keys()):
            self.domain_flag_default[flag_name] = default_value

    def get_all_flag_names(self) -> list[str]:
        """Returns a list of all the flag names"""
        return self.all_flag_names

    def get_domain_flag_defaults(self) -> dict[str, str]:
        """Returns a dictionary mapping each flag name to its default value"""
        return self.domain_flag_default

    def get_all_flag_domains(self) -> dict[str, str|list[str]|list[bool]]:
        """Returns a dictionary mapping all flag names to the domains that can be applied to them"""
        return self.flag_domains

    def get_flag_domain(self, flag_name: str) -> str|list[str]|list[bool]:
        """Returns a domain given a specific flag name"""
        return self.flag_domains[flag_name]

    def get_flag_default(self, flag_name: str) -> str|bool:
        return self.domain_flag_default[flag_name]
