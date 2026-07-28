#!/usr/bin/env bash
# Runs one benchmark case under one condition (hook|nohook).
# Usage: run_case.sh <cases.json> <case_id> <hook|nohook> <output_dir>
set -euo pipefail

CASES_JSON="$1"
CASE_ID="$2"
CONDITION="$3"   # hook | nohook
OUT_DIR="$4"
YUL_BIN="/home/aman/Desktop/chains/ai-bump/yul"

case_json() {
  jq -c --arg id "$CASE_ID" '.[] | select(.id == $id)' "$CASES_JSON"
}

C="$(case_json)"
if [ -z "$C" ]; then
  echo "case $CASE_ID not found" >&2
  exit 1
fi

MANIFEST=$(echo "$C" | jq -r '.manifest')
TYPE=$(echo "$C" | jq -r '.type')
PROMPT=$(echo "$C" | jq -r '.prompt')
SEED=$(echo "$C" | jq -r '.seed // empty')

WORKDIR="$OUT_DIR/$CASE_ID/$CONDITION"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR/.claude"

if [ "$TYPE" = "existing" ]; then
  printf '%s' "$SEED" > "$WORKDIR/$MANIFEST"
fi

if [ "$CONDITION" = "hook" ]; then
  cat > "$WORKDIR/.claude/settings.json" <<EOF
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "$YUL_BIN",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
EOF
else
  cat > "$WORKDIR/.claude/settings.json" <<EOF
{}
EOF
fi

cd "$WORKDIR"

claude -p "$PROMPT" \
  --permission-mode bypassPermissions \
  --setting-sources project \
  --output-format stream-json \
  --verbose \
  --no-session-persistence \
  > transcript.jsonl 2> stderr.log || true

if [ -f "$MANIFEST" ]; then
  cp "$MANIFEST" "final_manifest"
else
  echo "MANIFEST_NOT_WRITTEN" > final_manifest
fi

echo "done: $CASE_ID [$CONDITION] -> $WORKDIR"
