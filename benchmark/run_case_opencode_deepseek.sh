#!/usr/bin/env bash
# Runs one benchmark case under one condition (hook|nohook), same as
# run_case_opencode.sh, but against DeepSeek's API via OpenCode's built-in
# "deepseek" provider (models.dev catalog) instead of a self-hosted,
# OpenAI-compatible endpoint - no custom provider config needed.
#
# The actual `opencode run` happens inside a fresh Apptainer container per
# invocation (see opencode-sandbox.def/.sif) with only this run's own
# WORKDIR bind-mounted - a model's bash/read tools can't see sibling runs'
# directories at all, unlike the un-sandboxed version, where a run was
# caught `cat`-ing a completed sibling repetition's manifest instead of
# doing the task itself. Build the image once with:
#   apptainer build benchmark/opencode-sandbox.sif benchmark/opencode-sandbox.def
#
# Credentials come from OpenCode's own store (`opencode auth login`, saved
# to ~/.local/share/opencode/auth.json), not an env var - this script never
# reads or holds the API key, so it can't leak it. (Earlier versions passed
# DEEPSEEK_API_KEY through the environment; a run's bash tool dumped its own
# env and the real key ended up in a committed transcript. See the
# opencode-deepseek branch history.)
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
#   YUL_BIN       path to the yul binary the hook condition execs
#                 (default: "yul" on PATH; build one with `go build -o yul .`)
#   OPENCODE_BIN  path to the opencode binary (default: "opencode" on PATH)
set -euo pipefail

CASES_JSON="$1"
CASE_ID="$2"
CONDITION="$3"   # hook | nohook
OUT_DIR="$4"
MODEL_ID="${5:-deepseek/deepseek-v4-flash}"
REPEAT_INDEX="${6:-}"

YUL_BIN="${YUL_BIN:-yul}"
OPENCODE_BIN="${OPENCODE_BIN:-opencode}"
command -v "$OPENCODE_BIN" >/dev/null 2>&1 || { echo "opencode not found (set OPENCODE_BIN or put it on PATH)" >&2; exit 1; }
command -v apptainer >/dev/null 2>&1 || { echo "apptainer not found on PATH" >&2; exit 1; }
if [ "$CONDITION" = "hook" ]; then
  command -v "$YUL_BIN" >/dev/null 2>&1 || { echo "yul not found (set YUL_BIN or put it on PATH)" >&2; exit 1; }
fi
SIF_IMAGE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/opencode-sandbox.sif"
[ -f "$SIF_IMAGE" ] || { echo "$SIF_IMAGE not found - build it with: apptainer build $SIF_IMAGE $(dirname "$SIF_IMAGE")/opencode-sandbox.def" >&2; exit 1; }

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

# "deepseek" is a built-in OpenCode provider (models.dev catalog); it reads
# the credential from OpenCode's own store (see the top of this file), not
# an env var. write/edit checking is the published "opencode-yul" npm
# package (chains-project/yul's own opencode-yul/ subdirectory) instead of
# a hand-rolled copy - it downloads and caches its own pinned yul release
# binary (currently v0.0.14), independent of $YUL_BIN below.
if [ "$CONDITION" = "hook" ]; then
  cat > "$WORKDIR/opencode.json" <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-yul"]
}
EOF
else
  cat > "$WORKDIR/opencode.json" <<EOF
{
  "\$schema": "https://opencode.ai/config.json"
}
EOF
fi

if [ "$CONDITION" = "hook" ]; then
  # opencode-yul (above) only covers write/edit as of its current release -
  # it has no Bash case, so this local plugin fills that one gap plus our
  # own auth-store-read block (neither is upstream yet). Talks to $YUL_BIN
  # (our locally built binary), not opencode-yul's separately pinned one.
  cat > "$WORKDIR/.opencode/plugins/yul-bash.js" <<'EOF'
// Blocks two things opencode-yul's published plugin doesn't cover yet:
// 1. Bash writes to a dependency manifest (main.go's runHook handles
//    tool_name "Bash" itself; opencode-yul's toHookInput() only maps
//    write/edit, so this delegates bash the same way write/edit already
//    delegate to yul - see run_case_opencode.sh for the fuller original).
// 2. Reading OpenCode's own credential store, wherever the DeepSeek API
//    key lives (auth login, not an env var - see the top of this script).
const AUTH_STORE_RE = /\.local[/\\]share[/\\]opencode[/\\]auth\.json|opencode[/\\]auth\.json/i

function mentionsAuthStore(args) {
  if (typeof args === "string") return AUTH_STORE_RE.test(args)
  if (Array.isArray(args)) return args.some(mentionsAuthStore)
  if (args && typeof args === "object") return Object.values(args).some(mentionsAuthStore)
  return false
}

export const YulBashPlugin = async () => {
  const YUL_BIN = process.env.YUL_BIN || "yul"
  return {
    "tool.execute.before": async (input, output) => {
      const a = output.args
      if (mentionsAuthStore(a)) {
        throw new Error("yul: reading OpenCode's credential store is not permitted")
      }
      if (input.tool !== "bash") return
      const proc = Bun.spawn([YUL_BIN], { stdin: "pipe", stdout: "pipe", stderr: "pipe" })
      proc.stdin.write(JSON.stringify({ tool_name: "Bash", tool_input: { command: a.command || "" } }))
      proc.stdin.end()
      const [code, stderr] = await Promise.all([proc.exited, new Response(proc.stderr).text()])
      if (code === 2) throw new Error(stderr.trim() || "yul: blocked outdated dependency")
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

# Runs under Apptainer, one fresh container per run: --no-home plus binding
# only this run's own WORKDIR means the model's bash/read tools can't see
# sibling runs' directories at all (a real cross-run contamination bug
# found by review - a model literally `cat ../run-1/pom.xml`'d another
# repetition's already-corrected manifest instead of doing the task).
#
# Cache dirs: yul's release binary and the opencode-yul plugin package are
# shared read-write across all containers (safe to race on - worst case is
# a redundant re-download, no per-run data in either). Everything under
# .local/share/opencode (sessions, snapshots, its own log) is NOT shared -
# each run gets a throwaway one, with only auth.json bind-mounted in
# read-only from the real one, so the container can authenticate without
# ever seeing another run's session state or writing into the real one.
SHARED_CACHE="$OUT_DIR/.container-shared-cache"
mkdir -p "$SHARED_CACHE/yul" "$SHARED_CACHE/opencode-pkg"
CONTAINER_HOME=$(mktemp -d)
mkdir -p "$CONTAINER_HOME/.local/share/opencode"
if [ -f "$HOME/.local/share/opencode/auth.json" ]; then
  cp "$HOME/.local/share/opencode/auth.json" "$CONTAINER_HOME/.local/share/opencode/auth.json"
fi

apptainer exec \
  --home "$CONTAINER_HOME:/home/sandbox" \
  --bind "$WORKDIR:/work" \
  --bind "$SHARED_CACHE/yul:/home/sandbox/.cache/yul" \
  --bind "$SHARED_CACHE/opencode-pkg:/home/sandbox/.cache/opencode" \
  --bind "$(command -v "$OPENCODE_BIN"):/usr/local/bin/opencode:ro" \
  --bind "$(command -v "$YUL_BIN"):/usr/local/bin/yul:ro" \
  --env YUL_BIN=/usr/local/bin/yul \
  --pwd /work \
  "$SIF_IMAGE" \
  opencode run "$PROMPT" \
  --model "$MODEL_ID" \
  --auto \
  --format json \
  > "$TRANSCRIPT_TMP" 2> "$STDERR_TMP" || true

# Belt-and-suspenders: the yul-bash.js plugin above blocks reads of the
# auth store, but redact anything DeepSeek-key-shaped that slips through
# anyway (format is public: "sk-" + 32 hex chars) - this doesn't require
# knowing the actual configured key, so it still works after rotation.
sed -i -E 's/sk-[a-f0-9]{32}/***REDACTED-DEEPSEEK-API-KEY***/g' "$TRANSCRIPT_TMP" "$STDERR_TMP"

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
# transcript never records it, but its own runtime log does. Each run has
# its own throwaway container $HOME now, so this log is already isolated
# to this run alone - the sessionID filter is just extra safety.
OPENCODE_LOG="$CONTAINER_HOME/.local/share/opencode/log/opencode.log"
SESSION_ID=$(jq -r 'select(.sessionID != null) | .sessionID' transcript.jsonl 2>/dev/null | head -1)
if [ -n "$SESSION_ID" ] && [ -f "$OPENCODE_LOG" ]; then
  grep -F "session.id=$SESSION_ID" "$OPENCODE_LOG" | grep -E "providerID=|llm\.provider=" > model_used.log || true
else
  : > model_used.log
fi
rm -rf "$CONTAINER_HOME"

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
