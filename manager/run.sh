#!/bin/bash -eu

schedule_url_poll() {
  set +e
  sleep 5
  while true
  do
    curl -m60 -sSf $1 > /dev/null
    sleep $2
  done
}

cleanup() {
  pkill -P $$ >/dev/null
}

schedule_url_poll http://localhost:5000/feeds/refresh 900 &
schedule_url_poll http://localhost:5000/tasks/reschedule 3600 &

trap 'cleanup' EXIT

env FLASK_APP=manager.app flask run
