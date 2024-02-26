"""Methods to validate flag combinations/options are correct"""
from random import randint


#TODO: Implement validation of domain flags
def validate_flag_choices(flag_choices: dict[str, bool | str | list[str]]) -> dict[str, bool | str | list[str]]:
    flag_names = list(flag_choices.keys())
    if "-fkeep-inline-dllexport" in flag_names:
        del flag_choices["-fkeep-inline-dllexport"]  # Not supported by my configuration


    # Make sure compression level is in the right bounds
    flto_compression_level = int(flag_choices["-flto-compression-level"])
    if flto_compression_level < 0 or flto_compression_level > 19:
        flag_choices["-flto-compression-level"] = str(randint(0, 19))



    flag_choices["-fsection-anchors"] = flag_choices["-ftoplevel-reorder"] = flag_choices["-funit-at-a-time"] # Needs to be the same as the others

    return flag_choices

def validate_live_patching_issues(flag_choices: dict[str, bool|str|list[str]]) \
        -> dict[str, bool|str|list[str]]:
    """
    Validates and corrects flags connected to live patching
    (which is not very useful for performance purposes
    and turns off a lot of other more useful flags)
    """
    # if
    # flag_choices["-live-patching"] == "inline-clone":

    return flag_choices



"""
-flive-patching=inline-clone disables the following optimization flags:

-fwhole-program  -fipa-pta  -fipa-reference  -fipa-ra
-fipa-icf  -fipa-icf-functions  -fipa-icf-variables
-fipa-bit-cp  -fipa-vrp  -fipa-pure-const
-fipa-reference-addressable
-fipa-stack-alignment -fipa-modref

-flive-patching=inline-only-static disables the following additional optimization flags:
-fipa-cp-clone  -fipa-sra  -fpartial-inlining  -fipa-cp

"""