# A module to read a subset of flags with defined values
from core.flags import Flags
from reader.all_flags_reader import AllTypeFlagsReader
import helpers.constants as constants

class FlagConfigurationReader:
    def __init__(self, binary_flag_file: str, domain_flag_file: str):
        self.binary_flag_file = binary_flag_file
        self.domain_flag_file = domain_flag_file
        self.flag_configuration = {}
        self.flags_obj = Flags()

    def read_in_flags(self) -> None:
        # Read flags the values are provided for
        reader = AllTypeFlagsReader(self.binary_flag_file, self.domain_flag_file)
        reader.read_in_flags()
        # Set binary flags seen to true
        for flag in reader.get_all_binary_flag_names():
            self.flag_configuration[flag] = True
            self.flags_obj.add_flag(flag, [True, False], True)
        # Set domain flags to their "default" values
        for flag ,domain in reader.get_domain_flag_domains().items():
            self.flag_configuration[flag] = reader.domain_defaults[flag]
            self.flags_obj.add_flag(flag, domain, reader.domain_defaults[flag])

        # Read all possible flags
        reader = AllTypeFlagsReader(constants.ALL_BINARY_FLAGS_PATH, constants.ALL_DOMAIN_FLAGS_PATH)
        reader.read_in_flags()
        all_flags = reader.get_all_flag_names()
        all_domain_defaults = reader.get_all_domain_defaults()
        bin_flags = reader.get_all_binary_flag_names()

        # Fill in difference between all possible flags and the ones provided
        flags_not_read = set(all_flags) - set(self.flag_configuration.keys())
        for flag_name in flags_not_read:
            # For every flag not in the read ones - do false or default value.
            if flag_name in bin_flags:
                self.flag_configuration[flag_name] = False
                self.flags_obj.add_flag(flag_name, [True, False], False)
            else:
                self.flag_configuration[flag_name] = all_domain_defaults[flag_name]
                self.flags_obj.add_flag(flag_name,
                                        reader.flag_domains[flag_name],
                                        reader.domain_defaults[flag_name])

    def get_flag_configuration(self) -> dict[str, str|bool]:
        return self.flag_configuration

    def get_flag_obj(self) -> Flags:
        return self.flags_obj