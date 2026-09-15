# benchmark

`cases.json` is hand-written: prompts the maintainers made up to plausibly
trigger a stale pinned dependency.

## `cases-hallucination.json`: package hallucination, not stale versions

This is a different failure mode from `cases.json`, and **yul does not
currently detect it**. `cases.json` tests whether a pinned dependency that
*exists* is stale. `cases-hallucination.json` tests whether Claude names a
dependency that doesn't exist in the registry at all. Two things make this
file structurally different:

- **Detection gap**: `pkg/util/pins.Diff` treats "the resolver couldn't
  find this package" identically to a network error — it returns an error,
  and the `PreToolUse` hook fails open on any resolver error (see
  `CLAUDE.md`). So running this file today will show `hook` and `nohook`
  behaving identically: yul currently has no code path that distinguishes
  a confirmed-nonexistent package from a transient lookup failure and
  blocks the former. This file is useful for measuring the gap, not for
  demonstrating a capability that exists yet.
- **No fixed ground truth per prompt**: the natural source for this,
  [PackageHallucination](https://github.com/Spracks/PackageHallucination)
  (Spracklen, Wijewickrama, Sakib, Maiti, Viswanath & Jadliwala, USENIX
  Security 2025 — 16 LLMs, 576k code samples, Python and JavaScript),
  deliberately does **not** publish which package(s) each prompt actually
  caused a model to hallucinate — the authors' stated reason is that doing
  so would hand out a ready-made list of squattable package names. Only
  their prompts are open (MIT-licensed, `Data/{Python,JavaScript}/{LLM,SO}_{AT,LY}.json`
  in that repo). Every prompt in `cases-hallucination.json` is verbatim
  from `Data/Python/LLM_AT.json` (cited by `line_index` in each case's
  `source`), picked because it describes a real package's functionality
  without naming it — exactly the framing that induces hallucination.
  `likely_intended_package` is **our own inference** of the real, existing
  package each description matches (several are near-verbatim quotes of
  that package's own real PyPI tagline, e.g. tqdm, asn1crypto,
  requests-toolbelt) — it is not a label from the dataset, since the
  dataset withholds that.

To use this file: run a case, then check whatever package name Claude
actually wrote in `requirements.txt` against PyPI (`pypi.org/pypi/<name>/json`
returning 404 means it doesn't exist — a real hallucination) and against
`likely_intended_package` (a real name that isn't the one we guessed is
still fine; a nonexistent name is the interesting result either way).

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
