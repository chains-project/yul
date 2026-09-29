#!/usr/bin/env bash
#
# Provision a local MinGW-w64 cross toolchain for the
# x86_64-pc-windows-gnu Rust target without requiring root.
#
# The Debian packages below ship the platform-specific Windows import
# libraries (libkernel32.a, libuser32.a, libmsvcrt.a, ...), the CRT
# objects (crt2.o, ...), libgcc, and the binutils dlltool that rustc
# uses for `#[link(kind = "raw-dylib")]` in the windows/windows-sys crates.
#
# Everything is unpacked into $MINGW_PREFIX (default: $HOME/mingw) and is
# used by scripts/build-windows.sh.

set -euo pipefail

PREFIX="${MINGW_PREFIX:-$HOME/mingw}"
DEBIAN_MIRROR="${DEBIAN_MIRROR:-http://deb.debian.org/debian}"
POOL="$DEBIAN_MIRROR/pool/main"

case "$(uname -m)" in
  aarch64) DEBARCH="arm64" ;;
  x86_64)  DEBARCH="amd64" ;;
  *) echo "unsupported host architecture: $(uname -m)" >&2; exit 1 ;;
esac

HOST_LIBDIR="$(uname -m)-linux-gnu"

packages=(
  "m/mingw-w64/mingw-w64-x86-64-dev_10.0.0-3_all.deb"
  "m/mingw-w64/mingw-w64-common_10.0.0-3_all.deb"
  "b/binutils-mingw-w64/binutils-mingw-w64-x86-64_2.40-2+10.4_${DEBARCH}.deb"
  "g/gcc-mingw-w64/gcc-mingw-w64-x86-64-posix_12.2.0-14+deb12u1+25.2+b1_${DEBARCH}.deb"
  "g/gcc-mingw-w64/gcc-mingw-w64-base_12.2.0-14+deb12u1+25.2+b1_${DEBARCH}.deb"
  "i/isl/libisl23_0.25-1.1_${DEBARCH}.deb"
  "m/mpclib3/libmpc3_1.3.1-1_${DEBARCH}.deb"
  "m/mpfr4/libmpfr6_4.2.0-1_${DEBARCH}.deb"
)

if [[ -x "$PREFIX/usr/bin/x86_64-w64-mingw32-gcc" && "${FORCE:-0}" != "1" ]]; then
  echo "MinGW-w64 toolchain already present in $PREFIX"
  exit 0
fi

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

mkdir -p "$PREFIX"
for pkg in "${packages[@]}"; do
  file="$workdir/$(basename "$pkg")"
  echo "fetching $(basename "$pkg")"
  curl -fsSL "$POOL/$pkg" -o "$file"
  dpkg-deb -x "$file" "$PREFIX"
done

ln -sf x86_64-w64-mingw32-gcc-posix "$PREFIX/usr/bin/x86_64-w64-mingw32-gcc"

echo
echo "MinGW-w64 toolchain installed in $PREFIX"
echo "Export the following before building (scripts/build-windows.sh does it for you):"
echo "  export PATH=\"$PREFIX/usr/bin:\$PATH\""
echo "  export LD_LIBRARY_PATH=\"$PREFIX/usr/lib/$HOST_LIBDIR\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}\""
