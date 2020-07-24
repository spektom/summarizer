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
	zip

for setup in $(ls */setup.sh); do
  $setup
done
