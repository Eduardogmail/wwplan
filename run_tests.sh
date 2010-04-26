#!/bin/bash
set -e

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:../build/debug
export PYTHONPATH=$PYTHONPATH:../build/debug:.
for TEST in $(ls test/*.py); do
  echo "$TEST"
  python $TEST
done
