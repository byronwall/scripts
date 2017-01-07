#!/bin/bash

# FIXME: Quote everything for whitespace!

# Note: mktemp instead of the other insecure alternatives
WORKDIR="$(mktemp -d)"
CURDIR="$PWD"
ORIGDIR="$(dirname "$1")"

cd "$WORKDIR"
unzip "$1"

# TODO: Sanity check: verify if we're at the top level of the epub

# Fix permissions; I've seen them wrong when unzipping an epub and
# they prevent all the next steps from being performed.
find . -type d -print0 | xargs -0 chmod 755
find . -type f -print0 | xargs -0 chmod 644

# Optimize PNGs
find . -iname "*.png" -print0 | xargs -0 optipng -o4
find . -iname "*.png" -print0 | xargs -0 advpng -z3
find . -iname "*.png" -print0 | xargs -0 advpng -z4
find . -iname "*.png" -print0 | xargs -0 advdef -z3
find . -iname "*.png" -print0 | xargs -0 advdef -z4

# Optimize JPGs
find . \( -iname "*.jpg" -o -iname "*.jpeg" \) -print0 | xargs -0 jpgcrush
find . \( -iname "*.jpg" -o -iname "*.jpeg" \) -print0 | xargs -0 jhead -purejpg

# Repack the epub. NOTE: The order and the options *ARE* important.
NEWNAME="$ORIGDIR/${1%%epub}new.epub"

zip -r -D -X -9 "$NEWNAME" mimetype META-INF OEBPS

# Optimize ZIPs
advzip -z3 "$NEWNAME"
advzip -z4 "$NEWNAME"

cd "$CURDIR"
echo rm -rf "$WORKDIR"
