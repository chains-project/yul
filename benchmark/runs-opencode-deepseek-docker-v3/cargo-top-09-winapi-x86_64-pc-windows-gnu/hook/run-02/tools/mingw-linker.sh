#!/usr/bin/env sh
# Linker shim for the x86_64-pc-windows-gnu target.
#
# Cargo/rustc invokes this to link Windows GNU binaries. It prefers a real
# MinGW-w64 cross linker on PATH and otherwise falls back to an extracted
# toolchain tree (set MINGW_W64_PREFIX, or see README.md).
set -eu

real="$(command -v x86_64-w64-mingw32-gcc || true)"
if [ -n "$real" ]; then
    exec "$real" "$@"
fi

prefix="${MINGW_W64_PREFIX:-}"
if [ -z "$prefix" ]; then
    for candidate in \
        /tmp/opencode/mingw \
        "$HOME/.local/mingw-w64" \
        /opt/mingw-w64; do
        if [ -x "$candidate/usr/bin/x86_64-w64-mingw32-gcc-posix" ]; then
            prefix="$candidate"
            break
        fi
    done
fi

if [ -n "$prefix" ]; then
    export GCC_EXEC_PREFIX="$prefix/usr/lib/gcc/"
    exec "$prefix/usr/bin/x86_64-w64-mingw32-gcc-posix" \
        "-B$prefix/usr/lib/gcc/" \
        "--sysroot=$prefix/usr/x86_64-w64-mingw32" \
        "$@"
fi

echo "error: x86_64-w64-mingw32-gcc not found; install MinGW-w64 or set MINGW_W64_PREFIX" >&2
exit 1
