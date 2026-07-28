# benchmark

Each case runs the scaffolding prompt non-interactively:

```
claude -p "$PROMPT" --permission-mode bypassPermissions \
  --setting-sources project --output-format stream-json --verbose \
  --no-session-persistence > transcript.jsonl 2> stderr.log
```

Two files come out of each run:

- `transcript.jsonl` - the full turn-by-turn record of the session (every
  assistant message, tool call, and tool result, including any `yul`
  block), one JSON object per line.
- `final_manifest` - a copy of whatever manifest file (`pom.xml`,
  `requirements.txt`, etc.) exists on disk once Claude finishes.
