#!/bin/bash

SCRIPT_DIR=$(dirname "$0")
VENV_PATH="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "Error : Virtual environment '$VENV_PATH' doesn't exist !"
    exit 1
fi
source "$VENV_PATH/bin/activate"
python "$SCRIPT_DIR/crawler_post_process_ner.py" --input /projects/ElasticStack_ia/labs/data/output/20-minutes-high-tech/clean --mode spacy_llm --api_key_file ../.secrets/openai_api_key.txt --config_file ./crawler_post_process_ner_spacy_llm.cfg --output_csv_file /projects/ElasticStack_ia/labs/data/spacy_llm.csv
deactivate