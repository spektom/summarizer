#!/bin/bash -eu

rm -f *.xpi

addon_id=$(jq -r .browser_specific_settings.gecko.id manifest.json)

zip -0 ${addon_id}.xpi \
  background.js \
  content.js \
  manifest.json
