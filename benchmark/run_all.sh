#!/usr/bin/env bash
# Runs all cases in cases.json under both hook and nohook conditions, in parallel.
# Usage: run_all.sh <cases.json> <output_dir> [parallelism] [repeats]
# [repeats] (default 1) runs each case/condition pair that many times, each
# into its own <case_id>/<condition>/repNN subdirectory (see run_case.sh).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES_JSON="$1"
OUT_DIR="$2"
JOBS="${3:-4}"
REPEATS="${4:-1}"

CASE_IDS=$(jq -r '.[].id' "$CASES_JSON")

for CASE_ID in $CASE_IDS; do
  for CONDITION in nohook hook; do
    if [ "$REPEATS" -gt 1 ]; then
      for REP in $(seq -w 1 "$REPEATS"); do
        echo "$CASE_ID $CONDITION $REP"
      done
    else
      echo "$CASE_ID $CONDITION 0"
    fi
  done
done | xargs -P "$JOBS" -n 3 bash -c "\"$SCRIPT_DIR/run_case.sh\" \"$CASES_JSON\" \"\$1\" \"\$2\" \"$OUT_DIR\" \"\$3\"" _
