#!/usr/bin/env bash
# Runs one benchmark case under one condition (hook|nohook), same as
# run_case_opencode.sh, but against DeepSeek's API via OpenCode's built-in
# "deepseek" provider (models.dev catalog) instead of a self-hosted,
# OpenAI-compatible endpoint - no custom provider config needed, just
# DEEPSEEK_API_KEY in the environment.
#
# Usage:
#   run_case_opencode_deepseek.sh <cases.json> <case_id> <hook|nohook> <output_dir> [model_id] [repeat_index]
#
#   model_id      opencode model spec provider/model (default:
#                 deepseek/deepseek-v4-flash).
#   repeat_index  if set, run output goes to <condition>/run-<repeat_index>/
#                 instead of directly under <condition>/ - use for repeated
#                 runs of the same case/condition.
#
# Env vars:
#   DEEPSEEK_API_KEY  required - DeepSeek API key (e.g. from .env)
#   YUL_BIN           path to the yul binary the hook condition execs
#                     (default: "yul" on PATH; build one with `go build -o yul .`)
#   OPENCODE_BIN      path to the opencode binary (default: "opencode" on PATH)
set -euo pipefail

CASES_JSON="$1"
CASE_ID="$2"
CONDITION="$3"   # hook | nohook
OUT_DIR="$4"
MODEL_ID="${5:-deepseek/deepseek-v4-flash}"
REPEAT_INDEX="${6:-}"

: "${DEEPSEEK_API_KEY:?DEEPSEEK_API_KEY must be set (see .env)}"

YUL_BIN="${YUL_BIN:-yul}"
OPENCODE_BIN="${OPENCODE_BIN:-opencode}"
command -v "$OPENCODE_BIN" >/dev/null 2>&1 || { echo "opencode not found (set OPENCODE_BIN or put it on PATH)" >&2; exit 1; }
if [ "$CONDITION" = "hook" ]; then
  command -v "$YUL_BIN" >/dev/null 2>&1 || { echo "yul not found (set YUL_BIN or put it on PATH)" >&2; exit 1; }
fi

case_json() {
  jq -c --arg id "$CASE_ID" '.[] | select(.id == $id)' "$CASES_JSON"
}

C="$(case_json)"
if [ -z "$C" ]; then
  echo "case $CASE_ID not found" >&2
  exit 1
fi

# .manifest is usually a single path, but a case may instead give an array
# of candidate paths - only meaningful for "fresh" cases, since an
# "existing" case needs one fixed path to seed.
MANIFEST=$(echo "$C" | jq -r 'if (.manifest|type)=="array" then .manifest[0] else .manifest end')
TYPE=$(echo "$C" | jq -r '.type')
PROMPT=$(echo "$C" | jq -r '.prompt')
SEED=$(echo "$C" | jq -r '.seed // empty')

WORKDIR="$OUT_DIR/$CASE_ID/$CONDITION"
if [ -n "$REPEAT_INDEX" ]; then
  WORKDIR="$WORKDIR/run-$REPEAT_INDEX"
fi
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR/.opencode/plugins"

if [ "$TYPE" = "existing" ]; then
  mkdir -p "$(dirname "$WORKDIR/$MANIFEST")"
  printf '%s' "$SEED" > "$WORKDIR/$MANIFEST"
fi

# No provider block needed - "deepseek" is a built-in OpenCode provider
# (models.dev catalog); it reads DEEPSEEK_API_KEY from the environment.
cat > "$WORKDIR/opencode.json" <<EOF
{
  "\$schema": "https://opencode.ai/config.json"
}
EOF

if [ "$CONDITION" = "hook" ]; then
  # Mirrors main.go's runHook: translate OpenCode's tool.execute.before
  # payload (write: filePath/content; edit: filePath/oldString/newString/
  # replaceAll) into yul's PreToolUse JSON shape, exec the binary, and
  # throw on exit 2 so OpenCode surfaces the stderr reason back to the
  # model - the same self-correction loop Claude Code's exit-2/stderr gives.
  cat > "$WORKDIR/.opencode/plugins/yul.js" <<'EOF'
// All the manifest/bash-bypass detection logic lives in main.go's runHook
// now (it handles Write, Edit, and Bash tool_names), so this plugin is just
// a thin translation layer: build yul's PreToolUse JSON shape from
// whichever OpenCode tool fired, spawn the binary, and throw on exit 2 so
// OpenCode surfaces the stderr reason back to the model - the same
// self-correction loop Claude Code's exit-2/stderr gives.
export const YulPlugin = async () => {
  const YUL_BIN = process.env.YUL_BIN || "yul"
  const check = async (payload) => {
    const proc = Bun.spawn([YUL_BIN], { stdin: "pipe", stdout: "pipe", stderr: "pipe" })
    proc.stdin.write(JSON.stringify(payload))
    proc.stdin.end()
    const [code, stderr] = await Promise.all([proc.exited, new Response(proc.stderr).text()])
    if (code === 2) throw new Error(stderr.trim() || "yul: blocked outdated dependency")
  }

  return {
    "tool.execute.before": async (input, output) => {
      const a = output.args
      if (input.tool === "bash") {
        await check({ tool_name: "Bash", tool_input: { command: a.command || "" } })
        return
      }
      if (input.tool !== "write" && input.tool !== "edit") return
      const payload = input.tool === "write"
        ? { tool_name: "Write", tool_input: { file_path: a.filePath, content: a.content } }
        : {
            tool_name: "Edit",
            tool_input: {
              file_path: a.filePath,
              old_string: a.oldString,
              new_string: a.newString,
              replace_all: !!a.replaceAll,
            },
          }
      await check(payload)
    },
  }
}
EOF
fi

cd "$WORKDIR"

# Cap `git rev-parse --show-toplevel` at WORKDIR so the model can't wander
# up into the real yul checkout and find real files that make it think the
# task's already done.
git init -q
git config user.email "benchmark@example.com"
git config user.name "benchmark"

# Captured to a tempfile outside WORKDIR, not directly to transcript.jsonl/
# stderr.log - the model's cwd is WORKDIR itself, so writing the live log
# there means the model can see (and, observed in practice, delete) its own
# run's log mid-session. Moved into place only after the run finishes.
TRANSCRIPT_TMP=$(mktemp)
STDERR_TMP=$(mktemp)
YUL_BIN="$YUL_BIN" "$OPENCODE_BIN" run "$PROMPT" \
  --model "$MODEL_ID" \
  --auto \
  --format json \
  > "$TRANSCRIPT_TMP" 2> "$STDERR_TMP" || true
mv "$TRANSCRIPT_TMP" transcript.jsonl
mv "$STDERR_TMP" stderr.log

# Per-run token/cost summary, aggregated from each step's usage. cost_usd
# is DeepSeek's real dollar cost as OpenCode's pricing table reports it.
jq -s '
  [.[] | select(.type=="step_finish")] as $steps
  | {
      llm_calls: ($steps | length),
      tokens: {
        input: ($steps | map(.part.tokens.input // 0) | add // 0),
        output: ($steps | map(.part.tokens.output // 0) | add // 0),
        cache_read: ($steps | map(.part.tokens.cache.read // 0) | add // 0),
        cache_write: ($steps | map(.part.tokens.cache.write // 0) | add // 0)
      },
      cost_usd: ($steps | map(.part.cost // 0) | add // 0)
    }
' transcript.jsonl > usage.json

# Direct proof of which provider/model actually served this run: OpenCode's
# transcript never records it, but its own runtime log does, per session.
# Filtered by this run's sessionID so concurrent runs sharing the same
# global log don't cross-contaminate.
OPENCODE_LOG="${OPENCODE_LOG_PATH:-$HOME/.local/share/opencode/log/opencode.log}"
SESSION_ID=$(jq -r 'select(.sessionID != null) | .sessionID' transcript.jsonl 2>/dev/null | head -1)
if [ -n "$SESSION_ID" ] && [ -f "$OPENCODE_LOG" ]; then
  grep -F "session.id=$SESSION_ID" "$OPENCODE_LOG" | grep -E "providerID=|llm\.provider=" > model_used.log || true
else
  : > model_used.log
fi

# When .manifest listed several candidate paths, use whichever one the
# model actually wrote.
FOUND_MANIFEST=""
shopt -s nullglob
while IFS= read -r candidate; do
  if [[ "$candidate" == *"*"* ]]; then
    matches=( $candidate )
    if [ ${#matches[@]} -gt 0 ]; then
      FOUND_MANIFEST="${matches[0]}"
      break
    fi
  elif [ -f "$candidate" ]; then
    FOUND_MANIFEST="$candidate"
    break
  fi
done < <(echo "$C" | jq -r 'if (.manifest|type)=="array" then .manifest[] else .manifest end')
shopt -u nullglob

if [ -n "$FOUND_MANIFEST" ]; then
  cp "$FOUND_MANIFEST" "final_manifest"
  echo "$FOUND_MANIFEST" > "final_manifest_path"
else
  echo "MANIFEST_NOT_WRITTEN" > final_manifest
fi

# Removed below so the run output doesn't end up with a nested-repo
# gitlink when committed.
rm -rf .git

echo "done: $CASE_ID [$CONDITION] -> $WORKDIR"
