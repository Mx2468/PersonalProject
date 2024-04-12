#!/bin/bash
conda run --live-stream -n PersonalProject python flag_controller.py -i ./test_cases/BenchmarksGame-fannkuchredux5.cpp -m genetic -n 25 --num-code-runs 5 --log-results &&
conda run --live-stream -n PersonalProject python flag_controller.py -i ./test_cases/BenchmarksGame-fannkuchredux5.cpp -m genetic -n 50 --num-code-runs 5 --log-results &&
conda run --live-stream -n PersonalProject python flag_controller.py -i ./test_cases/BenchmarksGame-fannkuchredux5.cpp -m genetic -n 75 --num-code-runs 5 --log-results
conda run --live-stream -n PersonalProject python flag_controller.py -i ./test_cases/BenchmarksGame-fannkuchredux5.cpp -m genetic -n 100 --num-code-runs 5 --log-results
