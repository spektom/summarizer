#!/bin/bash -eu

schedule_refresh() {
  set +e
  sleep 5
  while true
  do
    curl -sSf http://localhost:5000/feeds/refresh > /dev/null
    sleep 900
  done
}

schedule_refresh&

env FLASK_APP=manager.app flask run
