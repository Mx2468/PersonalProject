# A module to do a random exhaustive search of the flags for a compilation

from random import getrandbits
def random_search(flags: list[str]) -> dict[str, bool]:
    return {flag: bool(getrandbits(1)) for flag in flags}