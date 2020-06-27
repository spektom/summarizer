#!/bin/bash -eu

env FLASK_APP=summarizer.api FLASK_RUN_PORT=6000 flask run
