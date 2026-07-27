#!/usr/bin/env bash
# Runs all cases in cases.json under both hook and nohook conditions, in parallel.
# Usage: run_all.sh <cases.json> <output_dir> [parallelism]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES_JSON="$1"
OUT_DIR="$2"
JOBS="${3:-4}"

CASE_IDS=$(jq -r '.[].id' "$CASES_JSON")

for CASE_ID in $CASE_IDS; do
  for CONDITION in nohook hook; do
    echo "$CASE_ID $CONDITION"
  done
done | xargs -P "$JOBS" -n 2 bash -c "\"$SCRIPT_DIR/run_case.sh\" \"$CASES_JSON\" \"\$1\" \"\$2\" \"$OUT_DIR\"" _
