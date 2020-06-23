#!/bin/bash -eu

HOME=$(pwd)/.home

exec ./firefox/firefox --new-instance --headless --window-size 1920,1080 "$@"
