"""Methods to validate flag combinations/options are correct"""
from helpers import get_random_integer


#TODO: Implement validation of domain flags against their domains
def validate_flag_choices(flag_choices: dict[str, bool | str | list[str]]) -> dict[str, bool | str | list[str]]:
    flag_choices = validate_live_patching_issues(flag_choices)
    flag_choices = validate_link_time_optimisation_flags(flag_choices)

    # Not supported by my project's target configuration/architecture
    if "-fkeep-inline-dllexport" in flag_choices.keys():
        del flag_choices["-fkeep-inline-dllexport"]

    flag_choices["-fsection-anchors"] = flag_choices["-ftoplevel-reorder"] = flag_choices["-funit-at-a-time"] # Needs to be the same as the others

    # if "-ftree-parallelize-loops" in flag_choices.keys():
    #     print(f"-ftree-parallelize-loops value: {flag_choices['-ftree-parallelize-loops']}")
    return flag_choices

def validate_link_time_optimisation_flags(flag_choices: dict[str, bool | str | list[str]]) -> dict[str, bool | str | list[str]]:
    # Make sure compression level is in the right bounds
    flto_compression_level = int(flag_choices["-flto-compression-level"])
    if flto_compression_level < 0 or flto_compression_level > 19:
        flag_choices["-flto-compression-level"] = str(get_random_integer(0, 19))


    # Using this flag raises an error due to the lack of a linker with linker plugin support
    # Using -fno-fat-lto-objects seems to reduce performance
    # Removing the flag choice entirely and allowing the default to be calculated by g++ seems to make both problems go away
    if "-ffat-lto-objects" in flag_choices.keys():
        del flag_choices["-ffat-lto-objects"]

    return flag_choices


def validate_live_patching_issues(flag_choices: dict[str, bool|str|list[str]]) \
        -> dict[str, bool|str|list[str]]:
    """
    Validates and corrects flags connected to live patching.

    Live patching is incompatible with many flags that positively impact performance, hence the
    priority is to keep live-patching off if these flags are impacted. The level also impacted, as
    "inline-only-static" is more restrictive in the flags it allows than "inline-clone".
    """
    if "-flive-patching" in flag_choices.keys():
        if flag_choices["-flto"] == True:
            flag_choices["-flive-patching"] = "inline-clone"

        inline_clone_disabled_flags = ["-fwhole-program", "-fipa-pta", "-fipa-reference", "-fipa-ra",
            "-fipa-icf", "-fipa-bit-cp",  "-fipa-vrp", "-fipa-pure-const", "-fipa-reference-addressable",
            "-fipa-stack-alignment", "-fipa-modref"]

        inline_only_static_disabled_flags = ["-fipa-cp-clone", "-fipa-sra", "-fpartial-inlining", "-fipa-cp"]

        # Case where flags enabled clash with the "inline-clone" setting
        inline_clone_clash = any(map(lambda x: flag_choices[x] != False, inline_clone_disabled_flags))
        # Case where flags enabled clash with the "inline-only-static" setting
        inline_only_static_clash = any(map(lambda x: flag_choices[x] != False, inline_only_static_disabled_flags))

        # Disable live patching if it interferes with any of the more useful flags
        if inline_clone_clash or inline_only_static_clash:
            if "-flive-patching" in flag_choices.keys():
                del flag_choices["-flive-patching"]
        elif not inline_clone_clash and not inline_only_static_clash:
            flag_choices["-flive-patching"] = "inline-only-static"
        elif not inline_clone_clash:
            flag_choices["-flive-patching"] = "inline-clone"

    return flag_choices
