#!/usr/bin/env bash
# Runs one benchmark case under one condition (hook|nohook), same as
# run_case.sh, but drives OpenCode instead of Claude Code, pointed at a
# self-hosted, OpenAI-compatible model endpoint (e.g. the vLLM server from
# ~/llm-local/scripts/vllm_qwen3.6_35b_a3b.sbatch) via a custom provider.
#
# Usage:
#   run_case_opencode.sh <cases.json> <case_id> <hook|nohook> <output_dir> <base_url> [model_id]
#
#   base_url  OpenAI-compatible endpoint of the running server, e.g.
#             http://<node>:8001/v1 (find <node> with `squeue -u $USER`
#             once the vLLM sbatch job is running).
#   model_id  opencode model spec provider/model (default:
#             local/qwen3.6-35b-a3b, matching --served-model-name in the
#             sbatch script).
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
BASE_URL="${5:?usage: run_case_opencode.sh <cases.json> <case_id> <hook|nohook> <output_dir> <base_url> [model_id]}"
MODEL_ID="${6:-local/qwen3.6-35b-a3b}"
PROVIDER_ID="${MODEL_ID%%/*}"
MODEL_NAME="${MODEL_ID#*/}"

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
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR/.opencode/plugins"

if [ "$TYPE" = "existing" ]; then
  mkdir -p "$(dirname "$WORKDIR/$MANIFEST")"
  printf '%s' "$SEED" > "$WORKDIR/$MANIFEST"
fi

# Custom OpenAI-compatible provider pointed at the self-hosted server -
# same pattern OpenCode's docs use for llama.cpp/LM Studio/Ollama.
cat > "$WORKDIR/opencode.json" <<EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "provider": {
    "$PROVIDER_ID": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "local vLLM",
      "options": { "baseURL": "$BASE_URL", "apiKey": "dummy" },
      "models": { "$MODEL_NAME": { "name": "$MODEL_NAME" } }
    }
  }
}
EOF

if [ "$CONDITION" = "hook" ]; then
  # Mirrors main.go's runHook: translate OpenCode's tool.execute.before
  # payload (write: filePath/content; edit: filePath/oldString/newString/
  # replaceAll) into yul's PreToolUse JSON shape, exec the binary, and
  # throw on exit 2 so OpenCode surfaces the stderr reason back to the
  # model - the same self-correction loop Claude Code's exit-2/stderr gives.
  cat > "$WORKDIR/.opencode/plugins/yul.js" <<'EOF'
// Manifest basenames yul knows how to check, mirroring pkg/*'s Filename()
// values (githubactions workflows use MatchesPath instead of a fixed name,
// so they're matched separately below).
const MANIFEST_RE = /(^|[/\\ '"])(pom\.xml|requirements\.txt|pyproject\.toml|package\.json|go\.mod|Cargo\.toml|\.github\/workflows\/[^\s'"]+\.ya?ml)(?=[/\\ '"]|$)/
// Shell constructs that mutate a file's *content* on disk - not an
// exhaustive parse of bash, just enough to catch the bypass a live model
// actually used (`printf ... > requirements.txt`) plus its common cousins.
const WRITE_RE = />>?(?!&)|\btee\b|\bsed\s+-i|\bperl\s+-i|\bdd\s+of=|\bcp\s|\bmv\s/

export const YulPlugin = async () => {
  const YUL_BIN = process.env.YUL_BIN || "yul"
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "bash") {
        const cmd = output.args.command || ""
        if (MANIFEST_RE.test(cmd) && WRITE_RE.test(cmd)) {
          throw new Error(
            "yul: use the write or edit tool to modify dependency manifests, not bash " +
            "(bash writes bypass the outdated-dependency check)"
          )
        }
        return
      }
      if (input.tool !== "write" && input.tool !== "edit") return
      const a = output.args
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

      const proc = Bun.spawn([YUL_BIN], { stdin: "pipe", stdout: "pipe", stderr: "pipe" })
      proc.stdin.write(JSON.stringify(payload))
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

YUL_BIN="$YUL_BIN" "$OPENCODE_BIN" run "$PROMPT" \
  --model "$MODEL_ID" \
  --auto \
  --format json \
  > transcript.jsonl 2> stderr.log || true

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
