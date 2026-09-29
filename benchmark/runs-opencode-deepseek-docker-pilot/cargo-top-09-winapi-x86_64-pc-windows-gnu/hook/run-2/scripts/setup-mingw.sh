#!/usr/bin/env bash
#
# Fetch a standalone MinGW-w64 toolchain (llvm-mingw) that supplies the
# x86_64-pc-windows-gnu linker, CRT objects and Windows API import libraries
# needed to cross-compile this crate from Linux/macOS.
set -euo pipefail

LLVM_MINGW_VERSION="${LLVM_MINGW_VERSION:-20260922}"
PREFIX="${MINGW_PREFIX:-$HOME/toolchains/llvm-mingw}"

case "$(uname -s)" in
  Linux) : ;;
  *) echo "this script targets a Linux host (got $(uname -s))" >&2; exit 1 ;;
esac

case "$(uname -m)" in
  aarch64|arm64) asset_arch=aarch64 ;;
  x86_64|amd64)  asset_arch=x86_64 ;;
  *) echo "unsupported host architecture: $(uname -m)" >&2; exit 1 ;;
esac

asset="llvm-mingw-${LLVM_MINGW_VERSION}-ucrt-ubuntu-22.04-${asset_arch}.tar.xz"
url="https://github.com/mstorsjo/llvm-mingw/releases/download/${LLVM_MINGW_VERSION}/${asset}"
extracted="llvm-mingw-${LLVM_MINGW_VERSION}-ucrt-ubuntu-22.04-${asset_arch}"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "==> downloading $url"
curl -fL --proto '=https' --tlsv1.2 -o "$tmp/$asset" "$url"

mkdir -p "$(dirname "$PREFIX")"
rm -rf "$PREFIX" "$(dirname "$PREFIX")/$extracted"

echo "==> extracting to $PREFIX"
if tar -xf "$tmp/$asset" -C "$(dirname "$PREFIX")" 2>/dev/null; then
  :
else
  python3 - "$tmp/$asset" "$(dirname "$PREFIX")" <<'PY'
import sys, tarfile
tarfile.open(sys.argv[1], "r:xz").extractall(sys.argv[2])
PY
fi
mv "$(dirname "$PREFIX")/$extracted" "$PREFIX"

# llvm-mingw ships compiler-rt/libunwind instead of GCC's libgcc, but Rust's
# windows-gnu target still passes -lgcc/-lgcc_eh to the linker. Provide shims.
echo "==> adding libgcc compatibility shims"
builtins="$(find "$PREFIX/lib/clang" -name 'libclang_rt.builtins-x86_64.a' | head -n1)"
ln -sf "$builtins" "$PREFIX/x86_64-w64-mingw32/lib/libgcc.a"
ln -sf libunwind.a "$PREFIX/x86_64-w64-mingw32/lib/libgcc_eh.a"

# Expose the cross tools where Cargo looks for linkers by default.
echo "==> linking cross tools into $HOME/.cargo/bin"
mkdir -p "$HOME/.cargo/bin"
for tool in gcc g++ ar dlltool windres ld nm objcopy ranlib strip as size objdump; do
  ln -sf "$PREFIX/bin/x86_64-w64-mingw32-$tool" "$HOME/.cargo/bin/x86_64-w64-mingw32-$tool"
done

echo "==> done. Build with: cargo build --release"
