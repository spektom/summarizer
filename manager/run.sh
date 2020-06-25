#!/bin/bash -eu

schedule_url_poll() {
  set +e
  sleep $(shuf -i 5-30 -n 1)
  while true
  do
    curl -m300 -sSf $1 > /dev/null
    sleep $2
  done
}

schedule_db_backup() {
  set +e
  while true
  do
    sleep $1
    version=$(date +"%Y%m%d%H")
    sqlite3 manager.db ".backup manager.bak.${version}"
  done
}

cleanup() {
  pkill -P $$ >/dev/null
}

schedule_url_poll http://localhost:5000/feeds/refresh 900 &
schedule_url_poll http://localhost:5000/tasks/reschedule 3600 &
schedule_db_backup 10800&

trap 'cleanup' EXIT

env FLASK_APP=manager.app flask run
