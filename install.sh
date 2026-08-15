#!/bin/sh
# Installs the yul binary from a chains-project/yul GitHub Release.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/chains-project/yul/main/install.sh | sh
#
# Env vars:
#   YUL_VERSION      release tag to install, e.g. "v0.2.0" (default: latest)
#   YUL_INSTALL_DIR  directory to install the binary into (default: ~/.local/bin)
set -eu

repo="chains-project/yul"
install_dir="${YUL_INSTALL_DIR:-"$HOME/.local/bin"}"
version="${YUL_VERSION:-}"

log() { printf '%s\n' "$*" >&2; }
die() {
	log "install.sh: $*"
	exit 1
}

need_cmd() {
	command -v "$1" >/dev/null 2>&1 || die "'$1' is required but not installed"
}

need_cmd curl
need_cmd tar

os="$(uname -s)"
case "$os" in
Linux) os=linux ;;
Darwin) os=darwin ;;
*) die "unsupported OS: $os (yul only publishes linux/darwin binaries)" ;;
esac

arch="$(uname -m)"
case "$arch" in
x86_64 | amd64) arch=amd64 ;;
aarch64 | arm64) arch=arm64 ;;
*) die "unsupported architecture: $arch (yul only publishes amd64/arm64 binaries)" ;;
esac

if [ -z "$version" ]; then
	version="$(curl -fsSL "https://api.github.com/repos/${repo}/releases/latest" |
		grep '"tag_name"' | head -n1 | sed 's/.*"tag_name": *"\([^"]*\)".*/\1/')"
	[ -n "$version" ] || die "could not determine latest release; set YUL_VERSION to install a specific version"
fi

tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/yul.XXXXXX")"
trap 'rm -rf "$tmp_dir"' EXIT INT TERM

archive="yul_${os}_${arch}.tar.gz"
base_url="https://github.com/${repo}/releases/download/${version}"

log "downloading yul ${version} for ${os}/${arch}..."
curl -fsSL -o "$tmp_dir/$archive" "$base_url/$archive" ||
	die "failed to download $base_url/$archive (does release $version exist for $os/$arch?)"
curl -fsSL -o "$tmp_dir/checksums.txt" "$base_url/checksums.txt" ||
	die "failed to download checksums.txt for $version"

log "verifying checksum..."
(
	cd "$tmp_dir"
	expected="$(grep "  ${archive}\$" checksums.txt | cut -d' ' -f1)"
	[ -n "$expected" ] || die "no checksum entry for $archive"
	if command -v sha256sum >/dev/null 2>&1; then
		actual="$(sha256sum "$archive" | cut -d' ' -f1)"
	elif command -v shasum >/dev/null 2>&1; then
		actual="$(shasum -a 256 "$archive" | cut -d' ' -f1)"
	else
		die "need sha256sum or shasum to verify the download"
	fi
	[ "$expected" = "$actual" ] || die "checksum mismatch for $archive: expected $expected, got $actual"
)

tar -xzf "$tmp_dir/$archive" -C "$tmp_dir" yul

mkdir -p "$install_dir"
install -m 755 "$tmp_dir/yul" "$install_dir/yul" 2>/dev/null || {
	cp "$tmp_dir/yul" "$install_dir/yul"
	chmod 755 "$install_dir/yul"
}

log "installed yul ${version} to ${install_dir}/yul"

case ":$PATH:" in
*":$install_dir:"*) ;;
*) log "note: ${install_dir} is not on your PATH; add it, e.g. export PATH=\"${install_dir}:\$PATH\"" ;;
esac
