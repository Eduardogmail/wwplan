#!/bin/bash
set -e

NS3PATH=${NS3PATH:-..}
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${NS3PATH}/build/debug
export PYTHONPATH=$PYTHONPATH:${NS3PATH}/build/debug:.
for TEST in test/*.py; do
  echo "$TEST"
  python $TEST || true
done
