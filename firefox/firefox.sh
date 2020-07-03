#!/bin/bash -eu

HOME=$(pwd)/.home

run_firefox()
{
  ./firefox/firefox --new-instance --headless --window-size 1920,1080 "$@" &
  FF_PID=$!
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
    fi
  done
}

trap cleanup EXIT
run_firefox
watchdog
