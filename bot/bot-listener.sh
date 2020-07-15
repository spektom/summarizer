#!/bin/bash -eu

[ ! -d venv ] && ./setup.sh
if [ -z ${VIRTUAL_ENV+x} ]; then
  source venv/bin/activate
fi

env TOKEN=$(cat ~/.briefnewsbottoken) python -m bot.listener
