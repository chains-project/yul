#!/bin/sh
# SessionStart hook: make sure the yul binary pinned by the plugin version is
# in the cache, downloading it from GitHub Releases if not. Always exits 0 so
# a network failure never breaks session startup (the PreToolUse hook fails
# open until the binary exists).
#
# Also checks whether a newer yul release exists than the plugin version this
# install currently resolves to, and if so prints a top-level systemMessage
# (shown straight to the user's terminal, the same channel Claude Code uses
# for its own update notices) rather than hookSpecificOutput.additionalContext
# (which only Claude sees). The marketplace source for yul is unpinned, but
# Claude Code doesn't re-resolve a plugin's source on every session, so a
# user can otherwise sit on a stale cached version indefinitely with no
# signal that a newer one shipped.
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

# version_gt A B: true (exit 0) if dotted-numeric version A > B.
version_gt() {
	[ "$1" = "$2" ] && return 1
	highest="$(printf '%s\n%s\n' "$1" "$2" | sort -t. -k1,1n -k2,2n -k3,3n | tail -n1)"
	[ "$highest" = "$1" ]
}

latest_tag="$(curl -fsSL --max-time 5 "https://api.github.com/repos/chains-project/yul/releases/latest" 2>/dev/null |
	grep '"tag_name"' | head -n1 | sed 's/.*"tag_name": *"v\{0,1\}\([^"]*\)".*/\1/')"

if [ -n "$latest_tag" ] && version_gt "$latest_tag" "$version"; then
	notice="yul: a newer release (v${latest_tag}) is available; this session is running the cached v${version}. Run \`/plugin marketplace update chains-project\` (or reinstall the yul plugin) to pick it up."
	escaped="$(printf '%s' "$notice" | sed 's/\\/\\\\/g; s/"/\\"/g')"
	printf '{"systemMessage":"%s"}\n' "$escaped"
fi

exit 0
