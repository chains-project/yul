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

# .manifest is usually a single path, but a case may instead give an array
# of candidate paths (e.g. a pypi case that lets Claude pick between
# requirements.txt and pyproject.toml) - only meaningful for "fresh" cases,
# since an "existing" case needs one fixed path to seed.
MANIFEST=$(echo "$C" | jq -r 'if (.manifest|type)=="array" then .manifest[0] else .manifest end')
TYPE=$(echo "$C" | jq -r '.type')
PROMPT=$(echo "$C" | jq -r '.prompt')
SEED=$(echo "$C" | jq -r '.seed // empty')

WORKDIR="$OUT_DIR/$CASE_ID/$CONDITION"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR/.claude"

if [ "$TYPE" = "existing" ]; then
  mkdir -p "$(dirname "$WORKDIR/$MANIFEST")"
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

# Cap `git rev-parse --show-toplevel` at WORKDIR so Claude can't wander up
# into the real yul checkout and find real files (e.g. .github/workflows/)
# that make it think the task's already done.
git init -q
git config user.email "benchmark@example.com"
git config user.name "benchmark"

claude -p "$PROMPT" \
  --model sonnet \
  --permission-mode bypassPermissions \
  --setting-sources project \
  --output-format stream-json \
  --verbose \
  --no-session-persistence \
  > transcript.jsonl 2> stderr.log || true

# When .manifest listed several candidate paths, use whichever one Claude
# actually wrote (the case leaves the choice of manifest file - or, for a
# glob candidate like ".github/workflows/*.yml", the choice of filename too
# - up to it).
#
# Build/dependency dirs to skip when falling back to a recursive search
# below - they can contain a same-named manifest (a vendored crate's
# Cargo.toml, a venv's pyproject.toml, ...) that isn't the one Claude wrote.
PRUNE_EXPR=( -path "*/target/*" -o -path "*/node_modules/*" -o -path "*/.git/*" \
  -o -path "*/dist/*" -o -path "*/build/*" -o -path "*/venv/*" -o -path "*/.venv/*" \
  -o -path "*/__pycache__/*" -o -path "*/site-packages/*" -o -path "*/.tox/*" \
  -o -path "*/vendor/*" -o -path "*/.m2/*" -o -path "*/.gradle/*" -o -path "*/.cargo/*" )

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
  else
    # Not at the expected top-level path - for a "fresh" case, Claude may
    # have scaffolded the project into a subdirectory of its own naming
    # (e.g. `cargo new <name>` instead of `cargo init` in place). Fall back
    # to a recursive search for the same filename, skipping build/dep dirs.
    base="$(basename "$candidate")"
    nested=$(find . \( "${PRUNE_EXPR[@]}" \) -prune -o -type f -name "$base" -print 2>/dev/null \
      | awk '{ print length, $0 }' | sort -n | head -1 | cut -d' ' -f2-)
    if [ -n "$nested" ]; then
      FOUND_MANIFEST="$nested"
      break
    fi
  fi
done < <(echo "$C" | jq -r 'if (.manifest|type)=="array" then .manifest[] else .manifest end')
shopt -u nullglob

if [ -n "$FOUND_MANIFEST" ]; then
  cp "$FOUND_MANIFEST" "final_manifest"
  echo "$FOUND_MANIFEST" > "final_manifest_path"
else
  echo "MANIFEST_NOT_WRITTEN" > final_manifest
fi

# Removed below so the run output doesn't end up with a
# nested-repo gitlink when committed.
rm -rf .git

echo "done: $CASE_ID [$CONDITION] -> $WORKDIR"
