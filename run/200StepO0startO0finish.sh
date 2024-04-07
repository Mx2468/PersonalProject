#!/bin/bash
for filename in ./test_cases/*.cpp; do
  conda run --live-stream -n PersonalProject python flag_controller.py -i "$filename" -m random -n 200 --num-code-runs 5 --dont-start-with-o3 --dont-compare-with-o3 --log-results
  conda run --live-stream -n PersonalProject python flag_controller.py -i "$filename" -m genetic -n 20 --num-code-runs 5 --dont-start-with-o3 --dont-compare-with-o3 --log-results
  conda run --live-stream -n PersonalProject python flag_controller.py -i "$filename" -m gaussian -n 200 --num-code-runs 5 --dont-start-with-o3 --dont-compare-with-o3 --log-results
done
