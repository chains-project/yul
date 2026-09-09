#!/usr/bin/env bash
# Runs one BUMP case: pull its -pre image, extract the project, wire up
# yul as a PreToolUse+SessionStart hook, and ask Claude to upgrade the
# flagged dependency without naming a target version.
# Usage: run_bump_case.sh <cases.json> <case_id> <output_dir> <yul_bin> <runs_dir>
# output_dir holds the ephemeral, gitignored extraction/workdir; runs_dir
# (checked into git - small) gets a copy of this case's transcript.jsonl
# and stderr.log, so every run's evidence survives even though the
# extracted project tree doesn't.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES_JSON="$1"
CASE_ID="$2"
OUT_DIR="$3"
YUL_BIN="$4"
RUNS_DIR="$5"

# run_with_timeout SECONDS CMD... - no timeout(1)/gtimeout(1) on this box.
run_with_timeout() {
	local secs="$1"; shift
	"$@" &
	local pid=$!
	(
		sleep "$secs"
		kill -TERM "$pid" 2>/dev/null
		sleep 5
		kill -KILL "$pid" 2>/dev/null
	) &
	local watcher=$!
	wait "$pid"
	local status=$?
	kill "$watcher" 2>/dev/null
	wait "$watcher" 2>/dev/null
	return $status
}

case_json() {
	jq -c --arg id "$CASE_ID" '.[] | select(.id == $id)' "$CASES_JSON"
}

C="$(case_json)"
if [ -z "$C" ]; then
	echo "case $CASE_ID not found" >&2
	exit 1
fi

PROJECT=$(echo "$C" | jq -r '.project')
GROUP=$(echo "$C" | jq -r '.groupId')
ARTIFACT=$(echo "$C" | jq -r '.artifactId')
BEFORE_VERSION=$(echo "$C" | jq -r '.previousVersion')
IMAGE=$(echo "$C" | jq -r '.preImage')

CASE_DIR="$OUT_DIR/$CASE_ID"
RESULTS="$OUT_DIR/results.jsonl"
rm -rf "$CASE_DIR"
mkdir -p "$CASE_DIR"

record() {
	# record CONDITION STATUS AFTER_VERSION YUL_NOTE
	python3 -c '
import json, sys
condition, status, after, note = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
print(json.dumps({
    "id": sys.argv[5], "project": sys.argv[6], "group": sys.argv[7],
    "artifact": sys.argv[8], "before": sys.argv[9],
    "condition": condition, "status": status, "after": after, "yul": note,
}))
' "$1" "$2" "$3" "$4" "$CASE_ID" "$PROJECT" "$GROUP" "$ARTIFACT" "$BEFORE_VERSION" >> "$RESULTS"
}

echo "=== $CASE_ID ($PROJECT: $GROUP:$ARTIFACT) ==="

if ! run_with_timeout 300 docker pull "$IMAGE" >"$CASE_DIR/docker-pull.log" 2>&1; then
	echo "  pull failed"
	record "n/a" "pull_failed" "" ""
	exit 0
fi

WORKDIR=$(docker inspect "$IMAGE" --format '{{.Config.WorkingDir}}' 2>>"$CASE_DIR/docker-pull.log")
if [ -z "$WORKDIR" ] || [ "$WORKDIR" = "/" ]; then
	echo "  no usable WorkingDir"
	record "n/a" "no_workdir" "" ""
	docker rmi "$IMAGE" >/dev/null 2>&1
	exit 0
fi

CID=$(docker create "$IMAGE" 2>>"$CASE_DIR/docker-pull.log")
if [ -z "$CID" ]; then
	echo "  docker create failed"
	record "n/a" "create_failed" "" ""
	docker rmi "$IMAGE" >/dev/null 2>&1
	exit 0
fi

mkdir -p "$CASE_DIR/pre-src"
if ! docker cp "$CID:$WORKDIR/." "$CASE_DIR/pre-src" >>"$CASE_DIR/docker-pull.log" 2>&1; then
	echo "  docker cp failed"
	record "n/a" "cp_failed" "" ""
	docker rm "$CID" >/dev/null 2>&1
	docker rmi "$IMAGE" >/dev/null 2>&1
	exit 0
fi
docker rm "$CID" >/dev/null 2>&1
docker rmi "$IMAGE" >/dev/null 2>&1 # keep disk usage bounded across 50 cases

PROMPT="Upgrade the $GROUP:$ARTIFACT dependency in this project."

for CONDITION in hook nohook; do
	RUN_DIR="$CASE_DIR/$CONDITION"
	mkdir -p "$RUN_DIR/.claude"
	cp -R "$CASE_DIR/pre-src/." "$RUN_DIR/"

	if [ "$CONDITION" = "hook" ]; then
		cat > "$RUN_DIR/.claude/settings.json" <<EOF
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "$YUL_BIN scan", "timeout": 30 }] }
    ],
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{ "type": "command", "command": "$YUL_BIN", "timeout": 30 }]
      }
    ]
  }
}
EOF
	else
		echo '{}' > "$RUN_DIR/.claude/settings.json"
	fi
	(cd "$RUN_DIR" && git init -q && git config user.email "benchmark@example.com" && git config user.name "benchmark")

	RUN_STATUS="ok"
	if ! (
		cd "$RUN_DIR" &&
		run_with_timeout 360 claude -p "$PROMPT" \
			--permission-mode bypassPermissions \
			--setting-sources project \
			--output-format stream-json \
			--verbose \
			--no-session-persistence \
			>transcript.jsonl 2>stderr.log
	); then
		echo "  [$CONDITION] claude session failed/timed out"
		RUN_STATUS="timeout_or_error"
	fi
	rm -rf "$RUN_DIR/.git"

	# What version ended up in the dependency's own pom.xml (first match
	# with an adjacent <version> on the next line - good enough for this
	# survey).
	AFTER_VERSION=$(grep -rA1 "<artifactId>$ARTIFACT</artifactId>" --include=pom.xml "$RUN_DIR" 2>/dev/null |
		grep -o '<version>[^<]*</version>' | head -1 | sed -e 's/<version>//' -e 's/<\/version>//')

	YUL_NOTE="none"
	if [ "$CONDITION" = "nohook" ]; then
		YUL_NOTE="n/a"
	elif [ -f "$RUN_DIR/transcript.jsonl" ]; then
		if grep -qi "hallucinated version\|does not exist" "$RUN_DIR/transcript.jsonl" 2>/dev/null; then
			if grep -qi "\"$ARTIFACT\|$ARTIFACT version\|:$ARTIFACT " "$RUN_DIR/transcript.jsonl" 2>/dev/null; then
				YUL_NOTE="hallucination-flagged"
			else
				YUL_NOTE="flagged-other-dep"
			fi
		elif grep -q "outdated dependencies, use these versions instead" "$RUN_DIR/transcript.jsonl" 2>/dev/null; then
			YUL_NOTE="outdated-flagged-somewhere"
		fi
	fi

	record "$CONDITION" "$RUN_STATUS" "${AFTER_VERSION:-unknown}" "$YUL_NOTE"
	echo "  [$CONDITION] done: $BEFORE_VERSION -> ${AFTER_VERSION:-unknown} (yul: $YUL_NOTE)"

	# Preserve this run's transcript/stderr in the checked-in runs dir
	# before tearing down the (gitignored) extracted project tree.
	mkdir -p "$RUNS_DIR/$CASE_ID/$CONDITION"
	cp -f "$RUN_DIR/transcript.jsonl" "$RUNS_DIR/$CASE_ID/$CONDITION/transcript.jsonl" 2>/dev/null
	cp -f "$RUN_DIR/stderr.log" "$RUNS_DIR/$CASE_ID/$CONDITION/stderr.log" 2>/dev/null
done

# Keep disk bounded: drop the extracted sources now that both runs'
# evidence is safely copied out.
rm -rf "$CASE_DIR"
