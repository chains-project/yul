#!/usr/bin/env bash
# Provision an x86_64-w64-mingw32 GCC toolchain (compiler, binutils, CRT and
# Windows import libraries) on a Debian host, without root, by unpacking the
# distribution .deb packages into a local prefix.
#
# Requires: curl, xz-utils, dpkg-deb, python3
set -euo pipefail

SUITE="${SUITE:-trixie}"
MINGW_PREFIX="${MINGW_PREFIX:-$HOME/.local/opt/mingw-w64}"
ARCH="$(dpkg --print-architecture)"
BASE="https://deb.debian.org/debian"

PKGS=(
  mingw-w64-common
  mingw-w64-x86-64-dev
  gcc-mingw-w64-base
  gcc-mingw-w64-x86-64-posix
  gcc-mingw-w64-x86-64-posix-runtime
  binutils-mingw-w64-x86-64
)

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "Fetching Debian package index (${SUITE}/${ARCH})..."
curl -fsS "$BASE/dists/$SUITE/main/binary-$ARCH/Packages.xz" -o "$WORK/Packages.xz"

echo "Resolving package filenames..."
mapfile -t FILES < <(python3 - "$WORK/Packages.xz" "${PKGS[@]}" <<'PY'
import lzma, sys
path, *want = sys.argv[1:]
stanzas = lzma.open(path, "rt", encoding="utf-8", errors="replace").read().split("\n\n")
found = {}
for s in stanzas:
    fields = {}
    key = None
    for line in s.split("\n"):
        if line[:1] in (" ", "\t") and key:
            fields[key] += "\n" + line
        else:
            k, _, v = line.partition(": ")
            fields[k] = v
            key = k
    name = fields.get("Package")
    if name in want and name not in found:
        found[name] = fields.get("Filename")
for name in want:
    if name not in found:
        sys.exit(f"package not found: {name}")
    print(found[name])
PY
)

echo "Downloading and unpacking into $MINGW_PREFIX ..."
mkdir -p "$MINGW_PREFIX" "$WORK/debs"
for f in "${FILES[@]}"; do
  deb="$WORK/debs/$(basename "$f")"
  curl -fsS "$BASE/$f" -o "$deb"
  dpkg-deb -x "$deb" "$MINGW_PREFIX"
done

ln -sf x86_64-w64-mingw32-gcc-posix "$MINGW_PREFIX/usr/bin/x86_64-w64-mingw32-gcc"

# Expose the cross tools on PATH so cargo's configured linker/ar resolve.
BIN_DIR="$(dirname "$(command -v cargo)")"
[ -w "$BIN_DIR" ] || BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
for tool in "$MINGW_PREFIX"/usr/bin/x86_64-w64-mingw32-*; do
  ln -sf "$tool" "$BIN_DIR/$(basename "$tool")"
done

echo "Done. Toolchain installed at $MINGW_PREFIX"
echo "Cross tools linked into $BIN_DIR"
