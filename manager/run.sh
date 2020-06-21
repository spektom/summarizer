#!/bin/bash -eu

schedule_url_poll() {
  set +e
  sleep 5
  while true
  do
    curl -sSf $1 > /dev/null
    sleep $2
  done
}

schedule_url_poll http://localhost:5000/feeds/refresh 900 &
schedule_url_poll http://localhost:5000/tasks/reschedule 3600 &

env FLASK_APP=manager.app flask run
