#!/bin/bash -l
set -e
if [ "$#" -eq 0 ]; then
  miniwerk init
else
  exec "$@"
fi
