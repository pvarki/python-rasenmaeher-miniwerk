#!/bin/bash -l
set -e
if [ "$#" -eq 0 ]; then
  miniwerk --help
else
  exec "$@"
fi
