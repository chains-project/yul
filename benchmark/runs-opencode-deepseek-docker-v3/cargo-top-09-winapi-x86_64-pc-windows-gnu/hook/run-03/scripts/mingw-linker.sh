#!/usr/bin/env sh
# Linker wrapper for cross-compiling to x86_64-pc-windows-gnu.
#
# Uses the rust-lld shipped with the active toolchain (no external GNU ld
# required) and adds the search paths for the MinGW-w64 import libraries plus
# the GCC runtime (libgcc) that the windows-gnu target links against.
set -eu

root="$(cd "$(dirname "$0")/.." && pwd)"
sysroot="$(rustc --print sysroot)"
host="$(rustc -vV | sed -n 's/^host: //p')"
lld="$sysroot/lib/rustlib/$host/bin/rust-lld"

mingw="${MINGW_ROOT:-$root/.mingw}"

exec "$lld" "$@" \
    -L "$mingw/usr/x86_64-w64-mingw32/lib" \
    -L "$mingw/usr/lib/gcc/x86_64-w64-mingw32/14-posix"
