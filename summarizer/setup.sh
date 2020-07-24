#!/bin/bash -eu

if [ -d venv ]; then
  echo "Directory venv/ exists, nothing to do."
  exit
fi

trap "rm -rf venv" ERR

python3 -mvenv venv
source venv/bin/activate
pip install wheel
BLIS_ARCH=generic pip install -r requirements.txt --no-binary=blis
python -m spacy download en_core_web_lg
