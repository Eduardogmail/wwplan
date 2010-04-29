#!/bin/bash
set -e

PATCH="patches/ns-3-dev.$(date +%Y%m%d%H%M).patch"
(cd .. && hg diff src) > $PATCH
echo "Patch generated: $PATCH"
