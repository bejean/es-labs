#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
VENV_PATH="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "Error : Virtual environment '$VENV_PATH' doesn't exist !"
    exit 1
fi
source "$VENV_PATH/bin/activate"
python $SCRIPT_DIR/elasticsearch_indexer.py "$@"
deactivate