#!/bin/bash -eu

HOME=$(pwd)/.home
exec ./firefox/firefox --new-instance "$@"
