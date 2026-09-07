# benchmark

`cases.json` is hand-written: prompts the maintainers made up to plausibly
trigger a stale pinned dependency. `cases-real.json` instead grounds each
prompt in a real, citable source instead of an invented scenario:

- **Python** (`pypi-requirements` / `pypi-pyproject`): natural-language task
  descriptions lifted from [GitChameleon 2.0](https://github.com/mrcabbage972/GitChameleonBenchmark)
  (Misra et al., ACL 2026 / arXiv:2507.12367), a benchmark of 328 problems
  built from real, documented breaking changes across 26 popular libraries.
  GitChameleon itself tests the opposite of what yul does — it deliberately
  targets an *old* pinned version to check API backward-compatibility — so
  only the `problem` text and target library are reused here, stripped of
  that version-pin framing, as fresh-project prompts. Which pin (if any)
  Claude actually writes, and whether it's stale, is still resolved live
  against PyPI, exactly as `cases.json` does — there's no way to freeze
  "latest" into a static dataset.
- **Java/Maven** and **GitHub Actions**: no case-level natural-language
  benchmark exists for either ecosystem (BUMP records commits, not prompts,
  and nothing comparable exists for Actions), so instead of writing a
  purpose description by hand, every prompt is the **verbatim title of a
  real, verified `dependabot[bot]`/`renovate[bot]` pull request** that
  bumped that exact dependency/action in a real public repo — fetched and
  checked against the live PR, not reconstructed. The dependency/action
  choice itself is grounded in real frequency data: Maven picks (`slf4j-api`,
  `jackson-databind`, `spring-core`, ...) come from occurrence counts in
  [BUMP](https://github.com/chains-project/bump) (Reyes, Gamage, Skoglund,
  Baudry & Monperrus, SANER 2024, arXiv:2401.09906) — 571 reproducible real
  breaking dependency updates mined from 153 real Java projects; GitHub
  Actions picks (`checkout`, `setup-python`, `cache`, ...) come from Decan &
  Mens, "On the outdatedness of workflows in the GitHub Actions ecosystem"
  (Journal of Systems and Software, 2023, ~1M real workflows mined) plus
  Codecov's marketplace usage writeup. Each case's seed manifest pins the
  exact old version the real PR bumped *from*, and the prompt names the
  exact version the real PR bumped *to* — which, since these are historical
  PRs, is itself now stale. That directly exercises yul's core claim: even
  told to bump to a specific *real, once-current* version, it should push
  past that to whatever is actually latest today.
- **Python**: unlike Maven/Actions, GitChameleon's `problem` field *is*
  natural-language task text (not a commit/PR title), so those prompts are
  reworded from that field rather than quoted verbatim — see below.

Each entry in `cases-real.json` carries a `source` field documenting the
paper/dataset, URL, and specific record it's grounded in (`example_id` for
GitChameleon; `dependency` plus the real `pr_url`/`pr_title`/`pr_author` for
Maven and GitHub Actions). `run_case.sh` ignores unknown fields, so `source`
is metadata only and doesn't affect execution.

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
