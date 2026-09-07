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
- **Java/Maven**: dependencies chosen by real frequency in
  [BUMP](https://github.com/chains-project/bump) (Reyes, Gamage, Skoglund,
  Baudry & Monperrus, SANER 2024, arXiv:2401.09906), a benchmark of 571
  reproducible real breaking dependency updates mined from 153 real Java
  projects. The dependency choice (e.g. `slf4j-api`, `jackson-databind`,
  `spring-core`) is grounded in that dataset's occurrence counts; the
  wrapping prompt is still written by hand since BUMP records commits, not
  natural-language task prompts.
- **GitHub Actions**: actions chosen by real usage frequency reported in
  Decan & Mens, "On the outdatedness of workflows in the GitHub Actions
  ecosystem" (Journal of Systems and Software, 2023) — a large-scale mining
  study of ~1M real workflows — supplemented by Codecov's marketplace usage
  writeup for popular third-party actions. No case-level natural-language
  benchmark exists for this ecosystem, so, as with Maven, only the action
  choice is externally grounded; prompts are hand-written.

Each entry in `cases-real.json` carries a `source` field documenting the
paper/dataset, URL, and specific record it's grounded in (`example_id` for
GitChameleon, `dependency` for BUMP). `run_case.sh` ignores unknown fields,
so `source` is metadata only and doesn't affect execution.

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
