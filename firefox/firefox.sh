#!/bin/bash -eu

HOME=$(pwd)/.home

run_firefox()
{
  ./firefox/firefox --new-instance --headless --window-size 1920,1080 "$@" &
  FF_PID=$!
  FF_START_TIME=$(date +%s)
}

cleanup() {
  pkill -P $$ >/dev/null
}

watchdog() {
  while true; do
    sleep 30
    if ! kill -0 $FF_PID >/dev/null 2>&1; then
      echo "Firefox is down, starting again"
      run_firefox
    elif [ $(($(date +%s) - $FF_START_TIME)) -gt 36000 ]; then # restart every 10 hrs
      kill $FF_PID
    fi
  done
}

trap cleanup EXIT
run_firefox
watchdog
