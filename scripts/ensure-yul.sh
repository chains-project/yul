#!/bin/sh
# SessionStart hook: make sure the yul binary pinned by the plugin version is
# in the cache, downloading it from GitHub Releases if not. Always exits 0 so
# a network failure never breaks session startup (the PreToolUse hook fails
# open until the binary exists).
set -u

root="${CLAUDE_PLUGIN_ROOT:-$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)}"

version="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$root/.claude-plugin/plugin.json" | head -n1)"
[ -n "$version" ] || exit 0

cache_root="${XDG_CACHE_HOME:-$HOME/.cache}/yul"
cache_dir="$cache_root/v${version}"

if [ ! -x "$cache_dir/yul" ]; then
	YUL_VERSION="v${version}" YUL_INSTALL_DIR="$cache_dir" sh "$root/install.sh" >/dev/null 2>&1 || true
fi

# Once the pinned binary is in place, prune caches left behind by other
# versions (each release adds ~8 MB and nothing else deletes them).
if [ -x "$cache_dir/yul" ]; then
	for dir in "$cache_root"/v*/; do
		[ -d "$dir" ] && [ "$dir" != "$cache_dir/" ] && rm -rf "$dir"
	done
fi
exit 0
