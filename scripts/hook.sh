#!/bin/sh
# PreToolUse hook wrapper: run the cached yul binary matching the plugin
# version. If the binary isn't there yet (first session still downloading,
# offline install), fail open like yul itself does on resolver errors.
set -u

root="${CLAUDE_PLUGIN_ROOT:-$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)}"

version="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$root/.claude-plugin/plugin.json" | head -n1)"
bin="${XDG_CACHE_HOME:-$HOME/.cache}/yul/v${version}/yul"

if [ -n "$version" ] && [ -x "$bin" ]; then
	exec "$bin"
fi

cat >/dev/null 2>&1 || true
exit 0
