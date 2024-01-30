"""Methods to validate flag combinations/options are correct"""

def validate_flag_choices(flag_choice: dict[str, bool]) -> dict[str, bool]:
    if "-fkeep-inline-dllexport" in flag_choice.keys():
        del flag_choice["-fkeep-inline-dllexport"]  # Not supported by my configuration
    flag_choice["-fsection-anchors"] = flag_choice["-ftoplevel-reorder"] = flag_choice["-funit-at-a-time"] # Needs to be the same as the others
    return flag_choice