#!/bin/bash -eu

sudo apt-get install -y \
  build-essential \
  jq \
  libffi-dev \
  libssl-dev \
  python3-dev \
  gfortran \
  liblapack-dev \
  libopenblas-dev \
  libxml2-dev \
  libxslt-dev \
  zip \
  sqlite3

for f in $(ls */setup.sh); do
  (cd $(dirname $f); ./setup.sh)
done
