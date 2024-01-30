class FlagChoices:
    all_flag_names: list[str]
    binary_flag_choices: dict[str, bool]

    def __init__(self, flags: list[str]):
        self.all_flag_names = []
        self.binary_flag_choices = {flag: False for flag in flags}

    def get_binary_flag_choices(self) -> dict[str, bool]:
        return self.binary_flag_choices

    def get_all_flag_names(self) -> list[str]:
        return self.all_flag_names
