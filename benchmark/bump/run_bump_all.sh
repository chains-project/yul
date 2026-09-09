#!/usr/bin/env bash
# Runs every case in cases50.json (or whichever cases file is given) through
# run_bump_case.sh, in parallel.
# Usage: run_bump_all.sh <cases.json> <output_dir> <runs_dir> <yul_bin> [parallelism]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES_JSON="$1"
OUT_DIR="$2"
RUNS_DIR="$3"
YUL_BIN="$4"
JOBS="${5:-4}"

mkdir -p "$OUT_DIR" "$RUNS_DIR"
: > "$OUT_DIR/results.jsonl"

jq -r '.[].id' "$CASES_JSON" | xargs -P "$JOBS" -I {} \
	bash "$SCRIPT_DIR/run_bump_case.sh" "$CASES_JSON" {} "$OUT_DIR" "$YUL_BIN" "$RUNS_DIR"

echo "=== all cases done, results in $OUT_DIR/results.jsonl ==="
