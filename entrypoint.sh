#!/usr/bin/env bash
set -e

if [ $# -eq 0 ]; then
    exec jupyter notebook \
        --ip=0.0.0.0 \
        --port=8888 \
        --no-browser \
        --allow-root \
        --NotebookApp.token=''
else
    exec python pipeline.py "$@"
fi
