#!/bin/sh
# SessionStart hook: run the cached yul binary's "scan" subcommand, which
# walks the whole project for outdated pinned dependencies (not just ones a
# Write/Edit just touched), caches the result for a week, and prints
# SessionStart hook JSON with the findings as additionalContext so Claude
# can ask the user whether to update them. Must run after ensure-yul.sh,
# which downloads the binary this execs. Fails open like hook.sh: if the
# binary isn't there yet, this is a no-op.
set -u

root="${CLAUDE_PLUGIN_ROOT:-$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)}"

version="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$root/.claude-plugin/plugin.json" | head -n1)"
bin="${XDG_CACHE_HOME:-$HOME/.cache}/yul/v${version}/yul"

if [ -n "$version" ] && [ -x "$bin" ]; then
	exec "$bin" scan
fi

cat >/dev/null 2>&1 || true
exit 0
