#!/bin/bash
conda run --live-stream -n PersonalProject python flag_controller.py -i ./test_cases/BenchmarksGame-fannkuchredux5.cpp -m genetic -n 250 --num-code-runs 5 --log-results &&
conda run --live-stream -n PersonalProject python flag_controller.py -i ./test_cases/BenchmarksGame-fannkuchredux5.cpp -m genetic -n 500 --num-code-runs 5 --log-results &&
conda run --live-stream -n PersonalProject python flag_controller.py -i ./test_cases/BenchmarksGame-fannkuchredux5.cpp -m genetic -n 750 --num-code-runs 5 --log-results &&
conda run --live-stream -n PersonalProject python flag_controller.py -i ./test_cases/BenchmarksGame-fannkuchredux5.cpp -m genetic -n 1000 --num-code-runs 5 --log-results
