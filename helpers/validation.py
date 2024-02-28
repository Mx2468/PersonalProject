"""Methods to validate flag combinations/options are correct"""
from random import randint


#TODO: Implement validation of domain flags
def validate_flag_choices(flag_choices: dict[str, bool | str | list[str]]) -> dict[str, bool | str | list[str]]:

    flag_choices = validate_live_patching_issues(flag_choices)

    # Not supported by my configuration
    if "-fkeep-inline-dllexport" in flag_choices.keys():
        del flag_choices["-fkeep-inline-dllexport"]

    # Make sure compression level is in the right bounds
    flto_compression_level = int(flag_choices["-flto-compression-level"])
    if flto_compression_level < 0 or flto_compression_level > 19:
        flag_choices["-flto-compression-level"] = str(randint(0, 19))

    flag_choices["-fsection-anchors"] = flag_choices["-ftoplevel-reorder"] = flag_choices["-funit-at-a-time"] # Needs to be the same as the others

    return flag_choices

def validate_live_patching_issues(flag_choices: dict[str, bool|str|list[str]]) \
        -> dict[str, bool|str|list[str]]:
    """
    Validates and corrects flags connected to live patching.

    Live patching is incompatible with many flags that positively impact performance, hence the
    priority is to keep live-patching off if these flags are impacted. The level also impacted, as
    "inline-only-static" is more restrictive in the flags it allows than "inline-clone".
    """
    inline_clone_disabled_flags = ["-fwhole-program", "-fipa-pta", "-fipa-reference", "-fipa-ra",
        "-fipa-icf", "-fipa-icf-functions", "-fipa-icf-variables", "-fipa-bit-cp",  "-fipa-vrp",
        "-fipa-pure-const", "-fipa-reference-addressable", "-fipa-stack-alignment", "-fipa-modref"]

    inline_only_static_disabled_flags = ["-fipa-cp-clone", "-fipa-sra", "-fpartial-inlining", "-fipa-cp"]

    # Case where flags enabled clash with the "inline-clone" setting
    inline_clone_clash = any(map(lambda x: flag_choices[x] != False, inline_clone_disabled_flags))
    # Case where flags enabled clash with the "inline-only-static" setting
    inline_only_static_clash = any(map(lambda x: flag_choices[x] != False, inline_only_static_disabled_flags))

    # Disable live patching if it interferes with any of the more useful flags
    if inline_clone_clash or inline_only_static_clash:
        flag_choices["-flive-patching"] = False
    elif not inline_clone_clash and not inline_only_static_clash:
        flag_choices["-flive-patching"] = "inline-only-static"
    elif not inline_clone_clash:
        flag_choices["-flive-patching"] = "inline-clone"

    return flag_choices
