#!/usr/bin/env bash
#
# Build the crate for the x86_64-pc-windows-gnu target using the locally
# provisioned MinGW-w64 toolchain (run scripts/setup-mingw-w64.sh first).

set -euo pipefail

PREFIX="${MINGW_PREFIX:-$HOME/mingw}"
HOST_LIBDIR="$(uname -m)-linux-gnu"

if [[ ! -x "$PREFIX/usr/bin/x86_64-w64-mingw32-gcc" ]]; then
  echo "MinGW-w64 not found in $PREFIX; run scripts/setup-mingw-w64.sh" >&2
  exit 1
fi

export PATH="$PREFIX/usr/bin:$PATH"
export LD_LIBRARY_PATH="$PREFIX/usr/lib/$HOST_LIBDIR${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

exec cargo build --target x86_64-pc-windows-gnu "$@"
