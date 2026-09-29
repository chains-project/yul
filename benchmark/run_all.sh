#!/usr/bin/env bash
# Runs all cases in cases.json under both hook and nohook conditions, in parallel.
# Usage: run_all.sh <cases.json> <output_dir> [parallelism] [repeats] [ecosystem]
# [repeats] (default 1) runs each case/condition pair that many times, each
# into its own <case_id>/<condition>/repNN subdirectory (see run_case.sh).
# [ecosystem], if given, restricts the run to cases whose "ecosystem" field
# matches (e.g. "maven", "npm", "pypi", "golang", "cargo", "githubactions" -
# see each cases file's own "ecosystem" values, which differ slightly between
# cases.json and cases_top.json).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES_JSON="$1"
OUT_DIR="$2"
JOBS="${3:-4}"
REPEATS="${4:-1}"
ECOSYSTEM="${5:-}"

if [ -n "$ECOSYSTEM" ]; then
  CASE_IDS=$(jq -r --arg eco "$ECOSYSTEM" '.[] | select(.ecosystem == $eco) | .id' "$CASES_JSON")
  if [ -z "$CASE_IDS" ]; then
    echo "no cases found with ecosystem '$ECOSYSTEM' in $CASES_JSON" >&2
    exit 1
  fi
else
  CASE_IDS=$(jq -r '.[].id' "$CASES_JSON")
fi

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
