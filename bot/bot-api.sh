#!/bin/bash -eu

env TOKEN=$(cat ~/.briefnewsbottoken) \
  FLASK_APP=bot.api FLASK_RUN_PORT=7000 flask run
