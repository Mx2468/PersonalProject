#!/bin/bash
for filename in ./test_cases/*.cpp; do
  conda run --live-stream -n PersonalProject python flag_controller.py -i "$filename" -m random -n 1000 --num-code-runs 5 --dont-start-with-o3 --log-results
  conda run --live-stream -n PersonalProject python flag_controller.py -i "$filename" -m genetic -n 100 --num-code-runs 5 --dont-start-with-o3 --log-results
  conda run --live-stream -n PersonalProject python flag_controller.py -i "$filename" -m gaussian -n 1000 --num-code-runs 5 --dont-start-with-o3 --log-results
done
