#!/usr/bin/env bash
# Deterministic precision benchmark for yul's Maven hallucination check.
#
# For every fixture in fixtures.jsonl it builds a PreToolUse Write payload
# that adds one <dependency> to a fresh pom.xml, feeds it to the yul binary,
# and inspects yul's stderr. What matters is whether yul reported the
# dependency as *hallucinated* ("hallucinated package" / "hallucinated
# version"), NOT merely whether it blocked - a real-but-outdated pin also
# blocks, on the separate outdated-version check, and that is not a false
# positive here.
#
#   label = real          -> must NOT be reported hallucinated
#   label = fake-package  -> must be reported "hallucinated package"
#   label = fake-version  -> must be reported "hallucinated version"
#
# Hits repo1.maven.org (static CDN; the 200/404 and the maven-metadata.xml
# version list are deterministic). yul fails open on any other status or a
# transport error, which shows up as a missed fake, never a crash.
#
# Usage: run.sh [yul_binary]   (default: build ./ into a temp file)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FIXTURES="$SCRIPT_DIR/fixtures.jsonl"

YUL_BIN="${1:-}"
if [ -z "$YUL_BIN" ]; then
  YUL_BIN="$(mktemp -t yul.XXXXXX)"
  echo "building yul -> $YUL_BIN" >&2
  ( cd "$REPO_ROOT" && go build -o "$YUL_BIN" . )
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
POM_PATH="$WORK/pom.xml"   # must not exist -> every dep counts as new

tp=0 fp=0 tn=0 fn=0   # positive = "should be reported hallucinated"
printf '%-32s %-14s %-12s %-12s %s\n' FIXTURE LABEL EXPECT GOT RESULT

while IFS= read -r line; do
  [ -z "$line" ] && continue
  id=$(jq -r '.id'       <<<"$line")
  g=$(jq -r '.group'     <<<"$line")
  a=$(jq -r '.artifact'  <<<"$line")
  v=$(jq -r '.version'   <<<"$line")
  label=$(jq -r '.label' <<<"$line")

  pom="<project><modelVersion>4.0.0</modelVersion><groupId>x</groupId><artifactId>x</artifactId><version>1</version><dependencies><dependency><groupId>$g</groupId><artifactId>$a</artifactId><version>$v</version></dependency></dependencies></project>"
  payload=$(jq -nc --arg fp "$POM_PATH" --arg c "$pom" \
    '{tool_name:"Write", tool_input:{file_path:$fp, content:$c}}')

  rm -f "$POM_PATH"
  set +e
  err_out=$(echo "$payload" | "$YUL_BIN" 2>&1 >/dev/null)
  set -e
  sleep "${YUL_BENCH_DELAY:-0.2}"

  case "$err_out" in
    *"hallucinated package"*) got="halluc-pkg" ;;
    *"hallucinated version"*) got="halluc-ver" ;;
    *)                        got="not" ;;
  esac
  case "$label" in
    fake-package) expect="halluc-pkg" ;;
    fake-version) expect="halluc-ver" ;;
    *)            expect="not" ;;
  esac

  if   [ "$expect" != "not" ] && [ "$got" = "$expect" ]; then tp=$((tp+1)); res=ok
  elif [ "$expect" != "not" ] && [ "$got" = "not"     ]; then fn=$((fn+1)); res=MISS
  elif [ "$expect" != "not" ]                          ; then fn=$((fn+1)); res="MISS(wrong-kind:$got)"
  elif [ "$expect" = "not"  ] && [ "$got" = "not"     ]; then tn=$((tn+1)); res=ok
  else fp=$((fp+1)); res="FALSE-HALLUC($got)"
  fi

  printf '%-32s %-14s %-12s %-12s %s\n' "$id" "$label" "$expect" "$got" "$res"
done < "$FIXTURES"

echo
echo "confusion matrix (positive = 'should be reported hallucinated')"
printf '  true positives  (fake caught)        : %d\n' "$tp"
printf '  false negatives (fake missed)        : %d\n' "$fn"
printf '  true negatives  (real not flagged)   : %d\n' "$tn"
printf '  false positives (real flagged!)      : %d\n' "$fp"

den_p=$((tp+fp)); den_r=$((tp+fn))
[ "$den_p" -gt 0 ] && awk -v tp=$tp -v d=$den_p 'BEGIN{printf "  precision                            : %.3f\n", tp/d}'
[ "$den_r" -gt 0 ] && awk -v tp=$tp -v d=$den_r 'BEGIN{printf "  recall                              : %.3f\n", tp/d}'

[ "$fp" -eq 0 ] || { echo "FAIL: a real dependency was reported hallucinated"; exit 1; }
[ "$fn" -eq 0 ] || { echo "WARN: a fake dependency was missed (network fail-open?)"; exit 1; }
echo "OK"
