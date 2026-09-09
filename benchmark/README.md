# benchmark

`top_packages.sh [COUNT] [METRIC]` fetches the top `COUNT` (default 10)
packages per ecosystem, for every ecosystem yul supports that ecosyste.ms
also tracks (maven, pypi, npm, GitHub Actions, go, cargo), sorted by a
given ecosyste.ms popularity metric (default `dependent_repos_count`).
Useful for sourcing new `cases.json` candidates. See the script header for
details.

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
