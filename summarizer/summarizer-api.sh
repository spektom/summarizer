#!/bin/bash -eu

[ ! -d venv ] && ./setup.sh
if [ -z ${VIRTUAL_ENV+x} ]; then
  source venv/bin/activate
fi

env=""
if [ "$(uname -p)" = "aarch64" ]; then
  env="LD_PRELOAD=libgomp.so.1"
fi

env $env FLASK_APP=summarizer.app FLASK_RUN_PORT=6000 flask run
