#!/bin/bash -eu

HOME=$(pwd)/.home
./firefox/firefox --new-instance "$@"
