#!/bin/sh

set -e

NAME=smiusbdisplay
PAGE=https://www.siliconmotion.com/downloads/SM770-drivers.html
UA="Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
DIR=$(dirname "$(readlink -f "$0")")

fetch() {
    curl -fsSL -A "$UA" "$@"
}

HTML=$(fetch "$PAGE")
ZIP_URL=$(echo "$HTML" | grep -o 'href="[^"]*SMI-USB-Display-for-Linux-v[0-9.]*\.zip"' | head -1 | sed 's/^href="//; s/"$//')
NOTES_URL=$(echo "$HTML" | grep -o 'href="[^"]*release%20note%20for%20SM77x\.txt"' | head -1 | sed 's/^href="//; s/"$//')

[ -n "$ZIP_URL" ] || { echo "Unable to find the Linux driver in $PAGE" >&2; exit 1; }

VERSION=$(echo "$ZIP_URL" | sed 's/.*-v\([0-9.]*\)\.zip$/\1/')
echo "Latest release: $VERSION"

TMP=$(mktemp -d)
trap 'rm -fr "$TMP"' EXIT
cd "$TMP"

fetch -o driver.zip "$ZIP_URL"
unzip -q driver.zip

chmod +x SMIUSBDisplay-driver.*.run
./SMIUSBDisplay-driver.*.run --noexec --keep --nox11 --target $NAME-$VERSION > /dev/null 2>&1
chmod 0755 $NAME-$VERSION

rm -f $NAME-$VERSION/evdi.tar.gz
find $NAME-$VERSION -name "libusb*.so*" -delete

if [ -n "$NOTES_URL" ]; then
    fetch -o $NAME-$VERSION/release-notes.txt "$NOTES_URL"
fi

tar -cJf "$DIR/$NAME-$VERSION.tar.xz" $NAME-$VERSION
echo "Created $DIR/$NAME-$VERSION.tar.xz"
