#!/bin/sh
# SessionStart hook: make sure the yul binary pinned by the plugin version is
# in the cache, downloading it from GitHub Releases if not. Always exits 0 so
# a network failure never breaks session startup (the PreToolUse hook fails
# open until the binary exists).
set -u

root="${CLAUDE_PLUGIN_ROOT:-$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)}"

version="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$root/.claude-plugin/plugin.json" | head -n1)"
[ -n "$version" ] || exit 0

cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/yul/v${version}"
[ -x "$cache_dir/yul" ] && exit 0

YUL_VERSION="v${version}" YUL_INSTALL_DIR="$cache_dir" sh "$root/install.sh" >/dev/null 2>&1 || true
exit 0
