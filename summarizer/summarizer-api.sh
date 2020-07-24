#!/bin/bash -eu

[ ! -d venv ] && ./setup.sh
if [ -z ${VIRTUAL_ENV+x} ]; then
  source venv/bin/activate
fi

env FLASK_APP=summarizer.api FLASK_RUN_PORT=6000 FLASK_RUN_THREADED=False flask run
