#!/bin/bash -eu

FF_VERSION=77.0.1

if [ -d firefox ]; then
  echo "WARNING: Directory firefox/ already exists. To rebuild, remove the directory, then re-run the script."
else
  echo "Downloading Firefox version ${FF_VERSION}"
  wget -qc https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FF_VERSION}/linux-x86_64/en-US/firefox-${FF_VERSION}.tar.bz2

  echo "Extracting firefox-${FF_VERSION}.tar.bz2"
  tar -jxf firefox-${FF_VERSION}.tar.bz2

  echo "Patching omni.ja"
  cd firefox
  ../optimizejars.py --deoptimize /tmp/ ./ ./
  unzip -qq -d omni omni.ja
  cd omni
  sed -i 's|return this.matcher.matchesWindow(window);|return true; //\0|' modules/ExtensionContent.jsm
  zip -qr9XD ../omni.ja *
  cd ..
  rm -rf omni
  ../optimizejars.py --optimize /tmp/ ./ ./
  cd ..
fi

if [ -d .home ]; then
  echo "WARNING: Directory .home/ already exists. To rebuild, remove the directory, then re-run the script."
else
  echo "Installing extensions"
  wget -qc https://github.com/iamadamdev/bypass-paywalls-chrome/releases/latest/download/bypass-paywalls-firefox.xpi
  for f in *.xpi; do
    ./run.sh $f --first-startup
  done
fi
