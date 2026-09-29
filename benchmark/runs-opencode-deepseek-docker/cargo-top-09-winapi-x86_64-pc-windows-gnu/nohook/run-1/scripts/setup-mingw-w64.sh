#!/usr/bin/env bash
#
# Provision an unprivileged, user-space MinGW-w64 cross toolchain for the
# x86_64-pc-windows-gnu Rust target.
#
# Rust no longer ships the MinGW import libraries in its sysroot, and rustc's
# raw-dylib support for windows-gnu invokes `x86_64-w64-mingw32-dlltool` to
# synthesize the per-DLL import libraries that the Windows API bindings in
# crates such as `windows-sys` link against. This script fetches the matching
# Debian/Ubuntu packages and unpacks them under $MINGW_PREFIX without root.
#
# The tools are exposed through ~/.cargo/bin so cargo/rustc find them on PATH.

set -euo pipefail

host_arch="$(uname -m)"
case "$host_arch" in
    x86_64)  deb_arch="amd64" ;;
    aarch64) deb_arch="arm64" ;;
    *)
        echo "error: unsupported host architecture: $host_arch" >&2
        exit 1
        ;;
esac

MINGW_PREFIX="${MINGW_PREFIX:-$HOME/mingw}"
BIN_DIR="${CARGO_HOME:-$HOME/.cargo}/bin"
CODENAME="${DEBIAN_CODENAME:-bookworm}"
MIRROR="${DEBIAN_MIRROR:-http://deb.debian.org/debian}"

packages=(
    binutils-common
    binutils-mingw-w64-x86-64
    gcc-mingw-w64-base
    gcc-mingw-w64-x86-64-posix
    gcc-mingw-w64-x86-64-posix-runtime
    mingw-w64-common
    mingw-w64-x86-64-dev
    libisl23
    libmpc3
    libmpfr6
)

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

echo "Fetching package index for $CODENAME/$deb_arch ..."
curl -fsSL "$MIRROR/dists/$CODENAME/main/binary-$deb_arch/Packages.gz" \
    -o "$work/Packages.gz"

echo "Resolving download locations ..."
python3 - "$work/Packages.gz" "$work/filenames" "${packages[@]}" <<'PY'
import gzip, sys

index, out, wanted = sys.argv[1], sys.argv[2], set(sys.argv[3:])
found = {}
for block in gzip.open(index, "rt", errors="replace").read().split("\n\n"):
    if not block.strip():
        continue
    fields = {}
    for line in block.splitlines():
        if line and not line[0].isspace() and ": " in line:
            key, value = line.split(": ", 1)
            fields[key] = value
    name = fields.get("Package")
    if name in wanted and name not in found:
        found[name] = fields["Filename"]

missing = sorted(wanted - found.keys())
if missing:
    sys.stderr.write("missing packages: " + ", ".join(missing) + "\n")
    sys.exit(1)

with open(out, "w") as handle:
    for name in sorted(found):
        handle.write(found[name] + "\n")
PY

echo "Downloading and unpacking into $MINGW_PREFIX ..."
mkdir -p "$MINGW_PREFIX"
while read -r filename; do
    [[ -z "$filename" ]] && continue
    deb="$work/$(basename "$filename")"
    curl -fsSL "$MIRROR/$filename" -o "$deb"
    dpkg-deb -x "$deb" "$MINGW_PREFIX"
done < "$work/filenames"

mkdir -p "$BIN_DIR"

# The gcc package ships an unversioned driver only after update-alternatives
# runs, which dpkg-deb does not do; recreate it plus the usual tool aliases.
ln -sf "$MINGW_PREFIX/usr/bin/x86_64-w64-mingw32-gcc-posix" \
    "$MINGW_PREFIX/usr/bin/x86_64-w64-mingw32-gcc"

cat > "$BIN_DIR/x86_64-w64-mingw32-gcc" <<EOF
#!/bin/sh
prefix="$MINGW_PREFIX/usr"
export LD_LIBRARY_PATH="\$prefix/lib/$deb_arch-linux-gnu\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
export PATH="\$prefix/bin\${PATH:+:\$PATH}"
exec "\$prefix/bin/x86_64-w64-mingw32-gcc-posix" "\$@"
EOF
chmod +x "$BIN_DIR/x86_64-w64-mingw32-gcc"

for tool in dlltool ar ld nm objcopy strip windres as ranlib; do
    ln -sf "$MINGW_PREFIX/usr/bin/x86_64-w64-mingw32-$tool" \
        "$BIN_DIR/x86_64-w64-mingw32-$tool"
done

if ! grep -qs '.cargo/env' "$HOME/.profile" 2>/dev/null; then
    echo '. "$HOME/.cargo/env"' >> "$HOME/.profile"
fi
if ! grep -qs '.cargo/env' "$HOME/.bashrc" 2>/dev/null; then
    echo '. "$HOME/.cargo/env"' >> "$HOME/.bashrc"
fi

echo
echo "Done. MinGW-w64 installed under $MINGW_PREFIX"
echo "Run:  cargo build --target x86_64-pc-windows-gnu"
