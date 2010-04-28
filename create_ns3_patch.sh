#!/bin/bash
cd ..
hg diff src/ > wwplan/patches/ns-3-dev.$(date +%Y%m%d%H%M).patch
