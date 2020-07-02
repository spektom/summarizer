#!/bin/bash -eu

[ ! -d venv ] && ./setup.sh
if [ -z "${VIRTUAL_ENV}" ]; then
  source venv/bin/activate
fi

env TOKEN=$(cat ~/.briefnewsbottoken) \
  FLASK_APP=bot.api FLASK_RUN_PORT=7000 flask run
