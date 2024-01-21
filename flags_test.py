import os
from time import time
import subprocess
import flag_reader
import random_search

SOURCE_CODE_FILE = "./test_cases/BreadthFSSudoku.cpp"
COMPILED_CODE_FILE = "filetotest"

def time_needed(number_of_repititions: int, function_to_run: callable) -> float:
    """For measuring time"""
    start = time()
    for j in range(0, number_of_repititions):
        function_to_run()
    end = time()
    # time.time returns time in seconds, so conversion is not needed
    return (end-start)/number_of_repititions


def run_compiled_code():
    subprocess.run(f"./{COMPILED_CODE_FILE}", shell=True, cwd=os.getcwd())

def test_compilation_with_flag(function_to_benchmark: callable, opt_flag: str = "O0") -> float:
    subprocess.run([f"g++ {opt_flag} -w -I./csmith/include/ -o {COMPILED_CODE_FILE} {SOURCE_CODE_FILE}"],
                   shell=True, cwd=os.getcwd())
    return time_needed(3, function_to_benchmark)


def create_flag_string(flag_choices: dict[str, bool]) -> str:
    final_str = ""
    for flag_name, choice in flag_choices.items():
        if choice:
            final_str += f"{flag_name} "
        else:
            # Case where the flag is not chosen
            final_str += f"{flag_name.replace("-f", "-fno-", 1)} "

    return final_str

def validate_flag_choices(flag_choice: dict[str, bool]) -> dict[str, bool]:
    del flag_choice["-fkeep-inline-dllexport"]  # Not supported by my configuration
    flag_choice["-fsection-anchors"] = flag_choice["-ftoplevel-reorder"] = flag_choice["-funit-at-a-time"] # Needs to be the same as the others
    return flag_choice

def opt_loop(n: int, flags: list[str]) -> dict[str, bool]:
    fastest_time = None
    fastest_flags = None
    for i in range(n):
        flag_choice = random_search.random_search(flags)
        flag_choice = validate_flag_choices(flag_choice)
        current_time = test_compilation_with_flag(run_compiled_code, opt_flag=create_flag_string(flag_choice))
        if fastest_time is None or current_time < fastest_time:
            fastest_time = current_time
            fastest_flags = flag_choice
    return fastest_flags

if __name__ == '__main__':
    flags = flag_reader.read_binary_flags()
    #TODO - make a way for this to run indefinite numbers of times/anytime algorithm ( keep the definite number of times if possible just in case)
    fastest_flags = opt_loop(100, flags)
    print(fastest_flags)
    # print("Trying with O0")
    # o0 = test_compilation_with_flag(run_compiled_code, opt_flag="O0")
    # print("Trying with O1")
    # o1 = test_compilation_with_flag(run_compiled_code, opt_flag="O1")
    # print("Trying with O2")
    # o2 = test_compilation_with_flag(run_compiled_code, opt_flag="O2")
    # print("Trying with O3")
    # o3 = test_compilation_with_flag(run_compiled_code, opt_flag="O3")
    # print("Trying with Ofast")
    # ofast = test_compilation_with_flag(run_compiled_code, opt_flag="Ofast")
    # print("Trying with Os")
    # os_time = test_compilation_with_flag(run_compiled_code, opt_flag="Os")
    # print("Trying with Oz")
    # oz = test_compilation_with_flag(run_compiled_code, opt_flag="Oz")
    # print("Trying with Og")
    # og = test_compilation_with_flag(run_compiled_code, opt_flag="Og")
    #
    # print(f"Results:\n-O0: {o0}\n-O1: {o1}\n-O2 {o2}\n O3: {o3}\n Ofast: {ofast}\n-Os: {os_time}\n-Oz: {oz}\n-Og: {og}")