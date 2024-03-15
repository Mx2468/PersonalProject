"""A reader to combine the reading of both binary and domain flags"""
from reader.binary_flag_reader import BinaryFlagReader
from reader.domain_flag_reader import DomainFlagReader

class AllTypeFlagsReader:
    def __init__(self, binary_file_name, domain_file_name):
        """
        :param binary_file_name: The name of the binary flags file to import from
        :param domain_file_name: The name of the domain flags file to import from
        """
        self.all_flag_names = []
        self.bin_flag_names = []
        self.flag_domains = {}
        self.domain_defaults = {}
        self.binary_flag_path = binary_file_name
        self.domain_flag_path = domain_file_name

    def read_in_flags(self) -> None:
        """Read in the flags from both files provided"""
        with BinaryFlagReader(self.binary_flag_path) as bin_flags_reader:
            bin_flags_reader.read_in_flags()
            flag_names = bin_flags_reader.get_flags()
            self.all_flag_names += flag_names
            self.bin_flag_names += flag_names

        with DomainFlagReader(self.domain_flag_path) as domain_reader:
            domain_reader.read_in_flags()
            self.all_flag_names += domain_reader.get_flags()
            self.flag_domains.update(domain_reader.get_domains())
            self.domain_defaults.update(domain_reader.get_default_values())

    def get_all_flag_names(self) -> list[str]:
        """:return: A list of all flag names read in"""
        return self.all_flag_names

    def get_all_binary_flag_names(self) -> list[str]:
        """:return: A list of all binary flag names read in"""
        return self.bin_flag_names

    def get_all_domain_flag_names(self) -> list[str]:
        """:return: A list of all domain flags read in"""
        return list(self.flag_domains.keys())

    def get_all_domain_defaults(self):
        """:return: A list of all default values for the domain flags"""
        return self.domain_defaults

    def get_all_flag_domains(self) -> dict[str, str|list[str|bool]]:
        """:return: A dictionary containing all the flag names mapped to their domains"""
        bin_domains = {flag_name: [True, False] for flag_name in self.bin_flag_names}
        merged_domains = {**bin_domains, **self.flag_domains}
        return merged_domains

    def get_domain_flag_domains(self) -> dict[str, str|list[str]|list[bool]]:
        """:return: A dictionary"""
        return self.flag_domains