#!/bin/bash -eu

FF_VERSION=78.0b9

if [ -d firefox ]; then
  echo "WARNING: Directory firefox/ already exists. To rebuild, remove the directory, then re-run the script."
else
  echo "Downloading Firefox version ${FF_VERSION}"
  # Developer edition is required to allow installing unsigned addons
  wget -qc https://download-installer.cdn.mozilla.net/pub/devedition/releases/${FF_VERSION}/linux-x86_64/en-US/firefox-${FF_VERSION}.tar.bz2

  echo "Extracting firefox-${FF_VERSION}.tar.bz2"
  tar -jxf firefox-${FF_VERSION}.tar.bz2

  echo "Configuring firefox"
  cp autoconfig.js firefox/defaults/pref/
  cp config.js firefox/

  echo "Pre-installing extensions"
  mkdir -p firefox/distribution/extensions
  wget -cq -O firefox/distribution/extensions/bypasspaywalls@bypasspaywalls.weebly.com.xpi \
    https://github.com/iamadamdev/bypass-paywalls-chrome/releases/latest/download/bypass-paywalls-firefox.xpi
  wget -cq -O firefox/distribution/extensions/uBlock0@raymondhill.net.xpi \
    https://addons.mozilla.org/firefox/downloads/file/3579401/ublock_origin-1.27.10-an+fx.xpi
  (cd ../pagesaver; ./build.sh)
  mv ../pagesaver/*.xpi firefox/distribution/extensions

  echo "Patching omni.ja"
  cp firefox/omni.ja .
  ./optimizejars.py --deoptimize /tmp/ ./ ./ >/dev/null
  unzip -qq -d omni omni.ja
  sed -i 's|return this.matcher.matchesWindow(window);|return true; //\0|' omni/modules/ExtensionContent.jsm
  (cd omni ; zip -qr9XD ../omni.ja *)
  rm -rf omni
  ./optimizejars.py --optimize /tmp/ ./ ./ >/dev/null
  mv omni.ja firefox/

  echo "Removing old config"
  rm -rf .home
fi
