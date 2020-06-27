#!/bin/bash -eu

env TOKEN=$(cat ~/.briefnewsbottoken) python -m bot.listener
