# DeepSeek V4.1 Flash pilot, Docker runtime (full 60-case coverage)

Same idea as [`../runs-opencode-deepseek-pilot`](../runs-opencode-deepseek-pilot) (`yul` against real
dependency-addition tasks, once with the hook installed and once without, driven through
[OpenCode](https://opencode.ai) against DeepSeek's hosted API), but three things changed:

- **Sandboxed via Docker instead of Apptainer.** `benchmark/run_case_opencode_deepseek.sh` now
  auto-detects which container runtime is on `PATH` (`CONTAINER_RUNTIME=apptainer|docker` forces
  one) — added because Apptainer only runs on Linux and shares the host's own kernel/arch, which a
  Docker host can't guarantee (bind-mounting the host's `opencode` binary straight into the
  container failed with `exec format error` on a non-Linux host during testing; the Docker image now
  installs `opencode` natively at build time instead — see `benchmark/Dockerfile.opencode-sandbox`).
  Verified this doesn't change the isolation properties that matter: two different cases run
  concurrently under Docker produced fully independent session IDs, costs, and manifests, same as
  the Apptainer path already guaranteed.
- **All 60 cases in `cases_top.json` now, not just a 10-case subset** — but with uneven repetitions:
  the original 10-case subset (one per ecosystem pair, see below) has 3 reps; the other 50 have 1 rep
  each, orchestrated by `benchmark/run_deepseek_pilot.sh` (`CASE_IDS` env var overrides its hardcoded
  10-case default; fan-out via `xargs -P`, plus a watchdog that polls real `usage.json` cost every
  15s and kills the whole run if `COST_CAP_USD` is crossed). This means per-ecosystem sample sizes
  here are **not** directly comparable to a uniform-reps sweep (e.g. Claude Sonnet 5's 10-cases×3reps
  run in `bench/top-final-results`) — see the caveat in Results below.
- **`--thinking`'s reasoning content is actually captured here.** The original pilot's README noted
  `transcript.jsonl` never captured DeepSeek's actual reasoning, only a token count. This run's
  `transcript.jsonl` *does* carry real `type: "reasoning"` parts with full text — verified: every
  reasoning part in `transcript.jsonl` is mirrored exactly in `session_export.json`.

The model ID also changed on OpenCode's end, though the underlying model didn't:
`deepseek/deepseek-v4-flash` (used by the original pilot) has been renamed to `deepseek/deepseek-flash`
in the catalog — `opencode models deepseek` is the only reliable source of truth here, it's been
renamed before. Confirmed via OpenCode's own model metadata that both IDs across pilots point to the
same model name, `DeepSeek V4.1 Flash`; the *old* ID now silently resolves to a different, older
model (`DeepSeek V4 Flash`, released 2026-04-24) if used with a provider that still recognizes it, so
don't reuse it by habit.

Each run:

```
opencode run "$PROMPT" --model deepseek/deepseek-flash --auto --format json --thinking \
  > transcript.jsonl 2> stderr.log
```

Same five files per run as the original pilot (`transcript.jsonl`, `final_manifest`, `usage.json`,
`model_used.log`, `session_export.json`) — see that pilot's README for what each one contains. Heavy
generated build artifacts (`node_modules`, `.venv`, `target`, `.m2`, language caches, the
per-container OpenCode plugin install) are excluded from what's committed here; they're regenerable
scratch, not experiment data.

## Results

160 runs total (60 cases × 2 conditions, 10 cases × 3 reps + 50 cases × 1 rep), **0 failures**, real
cost **$1.238** ($0.400 for the 10-case×3-rep subset + $0.838 for the other 50 cases × 1 rep).

### Ground-truth methodology

Whether a rep's final manifest carries the *actual current latest* version of its target package
(one specific package per case, from `benchmark/top-packages.json`) is determined by
`benchmark/analyze_top_opencode.py` — a port of `analyze_top.py` (from the `bench/top-final-results`
branch, which produced the Claude Sonnet 5 numbers this run is meant to sit next to in the paper's
table) rewritten for OpenCode's transcript schema instead of `claude -p`'s. It works the same way:

1. Find the target package's pin in `final_manifest` (exact, range, or absent), per-ecosystem parsing
   rules mirroring `pkg/*/`'s own.
2. Run `yul scan --project-dir <rep>` on the rep directory — this is yul's own resolver, live network
   calls to each ecosystem's registry, reused as ground truth for "is this still outdated right now."
3. If the package isn't in yul's outdated list, the rep counts as *satisfied* — however it got there:
   the model already knew the right version (`native`), it looked it up via a registry/package-manager
   call visible in the transcript (`tool`), or `yul`'s `PreToolUse` hook blocked a stale write and the
   retry landed on the fix (`hook`) — the only one of the three that actually validates `yul`.

**Methodological caveat worth stating explicitly wherever this goes**: `yul scan` is `yul`'s own
resolver, so this measures "did the final state satisfy yul's own opinion of latest," not agreement
with an independent source. We tried building one — `benchmark/latest_version_oracle.py` queries
`packages.ecosyste.ms` directly — but it returned intermittent HTTP 402s for ~63% of the 60 target
packages (38-39/60) regardless of request pacing or retry count, well under its own advertised rate
limit (`X-RateLimit-Remaining` stayed in the thousands out of 5000) — looks like flakiness on
ecosyste.ms's backend, not something fixable from the client side. It resolved 22/60 packages
successfully; those 22 agreed with `yul scan`'s corresponding values everywhere they overlapped, which
is *some* independent corroboration, just not full coverage. The script is kept in the repo as a
documented, partially-working cross-check rather than deleted.

A rep's raw classification (`pin_kind`, `is_latest`, `how`) is in `analysis_rows.json` in this
directory, one row per rep — regenerate with the command in Reproducing below.

### Manual review

63 of 160 reps had the target package fully absent from the final manifest (not even a range) —
reviewed by hand, one case at a time, reading the actual generated source where the manifest alone
wasn't conclusive (full list and reasoning in `analyze_top_opencode.py`'s `EXCLUDED_REPS` /
`ALTERNATIVE_REPS`, keyed by case/condition/rep — **not** copied from `analyze_top.py`'s Claude-curated
lists, since DeepSeek's behavior differs on several of these):

- **28 reps excluded** (solved the task without the target dependency at all — wrote an equivalent
  implementation itself, confirmed by reading the generated source, not just the manifest). Notably
  concentrated in npm: `to-regex-range`, `fill-range`, `fs.realpath`, `supports-color`, `statuses`,
  `setprototypeof`, `unpipe`, and `resolve` were *all* reimplemented from scratch in at least one rep
  rather than depended on — small, single-purpose packages DeepSeek apparently considers easier to
  rewrite than pull in. Also `cargo-top-08-lazy_static` (used `std::sync::LazyLock`, a Rust 2024
  stdlib feature, instead of the crate), `go-top-03-go-spew` and `go-top-09-objx` (wrote their own
  pretty-printer / fluent map wrapper), and `pypi-top-09-click` (an argparse-based CLI with
  `dependencies = []`).
- **20 reps counted as satisfied via an equivalent alternative package** — most strikingly,
  **every single `maven-top-01-junit` rep** (6/6) used JUnit 5 (`org.junit.jupiter`) instead of the
  case's literal target, JUnit 4 (`junit:junit`) — the *exact same substitution* Claude Sonnet 5 made
  in its own run (see its `ALTERNATIVE_REPS`), suggesting this is a property of the prompt/ecosystem,
  not one model's idiosyncrasy. Also `maven-top-04-mysql-connector` (the renamed `mysql-connector-j`
  artifact), `maven-top-08-gson` (Jackson instead of Gson), `pypi-top-04-pytz` (`tzdata`),
  `cargo-top-03-winapi`/`cargo-top-09-winapi-x86_64-pc-windows-gnu` (the `windows-sys` crate),
  `ghactions-top-05-cache` (`setup-node`'s built-in `cache: npm`), `go-top-07-check-v1` (`testify`
  instead of `gopkg.in/check.v1`), and `go-top-06-x-net` (`github.com/coder/websocket`, a
  websocket-specific package, for one rep of a case about general networking primitives).
- **15 reps left as genuine misses**, not excluded or reclassified:
  - `ghactions-top-04-setup-python/hook/run-1`, `ghactions-top-09-docker-buildx/hook/run-2`,
    `go-top-05-testify/nohook/run-1`, `maven-top-09-kotlin-stdlib-jdk7/hook/run-1`: `MANIFEST_NOT_WRITTEN`,
    genuine completion failures.
  - `npm-top-10-fresh/hook/run-2`: `yul` blocked `fresh 0.5.2 -> 2.0.0` exactly as intended, but the
    model's retry *deleted* the dependency instead of fixing its version — a real hook-condition
    failure mode distinct from a near-miss on the version string.
  - `pypi-top-02-six` (both conditions): final `pyproject.toml` has only a `[build-system]` table, no
    `[project]` section at all — reads as an abandoned/incomplete solution, not a deliberate
    six-free approach.
  - `pypi-top-10-pandas` (both conditions): final manifest is a one-line `requirements.txt` containing
    only `requests==2.28.1` — completely unrelated to the CSV/tabular-data prompt.
  - `cargo-top-01-libc/nohook/run-2`: not a model miss — a harness limitation. The real manifest is at
    `systool/Cargo.toml`, a path `run_case_opencode_deepseek.sh`'s single-string `case.manifest` field
    never looks for (only the array-of-candidates form does). Doesn't change any table count either
    way: `libc = "0.2"` is a bare version (implicit range under Cargo), never going to count as an
    exact-pin "Task" regardless of whether the file was found.

### Table (paper format)

Same structure as the `Already-latest and mitigation counts per ecosystem` table:
**Tasks** = reps considered (total minus excluded); **Already latest** = satisfied without needing
the hook (`native` + `tool` + `alternative`); **Mitigated** = satisfied specifically because `yul`'s
hook blocked a stale write and the retry fixed it; **Rate** = Mitigated over stale candidates
(Tasks − Already latest, hook condition).

| Ecosystem | Tasks (nohook) | Already latest (nohook) | Tasks (hook) | Already latest (hook) | Mitigated | Rate |
| --- | --- | --- | --- | --- | --- | --- |
| Cargo | 11 | 10/11 | 11 | 11/11 | 0/0 | — |
| GitHub Actions | 14 | 2/14 | 14 | 2/14 | 9/12 | 75% |
| Go | 10 | 8/10 | 10 | 10/10 | 0/0 | — |
| Maven | 14 | 10/14 | 14 | 10/14 | 3/4 | 75% |
| npm | 4 | 2/4 | 4 | 3/4 | 0/1 | 0% |
| PyPI | 13 | 11/13 | 13 | 10/13 | 1/3 | 33% |
| **All** | **66** | **43/66** | **66** | **46/66** | **13/20** | **65%** |

**This is not directly comparable to a uniform-sample-size sweep** (see the repetition caveat above) —
`npm`'s Tasks dropped from a possible 14 to 4 because 10 of its 14 reps were excluded (reimplemented
rather than depended on, see Manual review), a far higher exclusion rate than any other ecosystem here
or in the Claude Sonnet 5 run.

**Rate is not uniformly 100% here**, unlike the Claude Sonnet 5 row in the paper's version of this
table. The clearest single cause is `npm-top-10-fresh/hook/run-2`'s dependency-deletion response to
being blocked (0/1 → 0% for npm); PyPI and Maven/GitHub Actions each have 1-3 stale candidates that
`yul`'s hook either never triggered on or triggered without the retry landing on latest — worth a
closer read of those specific transcripts before this goes in front of reviewers, since "the hook
fires but doesn't fully close the loop" is a different (and more interesting) finding than "the hook
never fires."

### Narrative findings from earlier passes over this data

**GitHub Actions is the most reliable ecosystem for the hook to act on** — `actions/checkout`-style
stale major-version tags get written from memory almost every time, `yul` blocks them, and the model's
retry lands on the SHA-pinned suggestion. The 25% miss on Rate here is worth checking case-by-case
before citing as "unreliable"; it may concentrate in one case (`ghactions-top-09-docker-buildx` flags
up to 4 actions per run, more surface area for one to slip through) rather than being spread evenly.

**The sandbox image (Apptainer and Docker both) has no per-ecosystem toolchains baked in** — only
`ca-certificates curl git jq nodejs npm python3`. Every Maven/Go/Cargo run has to self-bootstrap its
own JDK/Maven/Go/Rust from the internet inside the fresh, throwaway container — real per-run latency
that PyPI/npm/GitHub-Actions cases don't pay. Caught live in `maven-top-06-spring-data-jpa`: the model
downloaded JDK 17 and Maven 3.9.9 tarballs by hand, then ran Maven with an apparently-unresolved shell
variable as `-Dmaven.repo.local`, which silently wrote its ~90MB local repository cache into a
directory literally named `?` inside the workdir (excluded from what's committed here, along with all
other build caches). Worth deciding later whether to bake these toolchains into the sandbox image the
same way `opencode` now is for Docker.

## Reproducing

```sh
go build -o yul .
docker build -t yul-opencode-sandbox -f benchmark/Dockerfile.opencode-sandbox benchmark/
# or: apptainer build benchmark/opencode-sandbox.sif benchmark/opencode-sandbox.def
opencode auth login -p deepseek   # credential lives in OpenCode's own store, never an env var

# the original 10-case×3-rep subset:
REPS=3 OUT_DIR=/path/to/output COST_CAP_USD=10 bash benchmark/run_deepseek_pilot.sh

# the other 50 cases, 1 rep each:
CASE_IDS="$(jq -r '.[].id' benchmark/cases_top.json | grep -vFf <(printf '%s\n' \
  pypi-top-01-requests pypi-top-05-urllib3 maven-top-01-junit maven-top-06-spring-data-jpa \
  npm-top-04-to-regex-range npm-top-10-fresh go-top-06-x-net cargo-top-01-libc \
  ghactions-top-01-checkout ghactions-top-09-docker-buildx))" \
  REPS=1 OUT_DIR=/path/to/output COST_CAP_USD=10 bash benchmark/run_deepseek_pilot.sh

# ground-truth analysis (regenerate analysis_rows.json):
python3 benchmark/analyze_top_opencode.py /path/to/combined-output --yul ./yul \
  --json-out benchmark/runs-opencode-deepseek-docker-pilot/analysis_rows.json

# independent cross-check (partial - see the 402 caveat above):
python3 benchmark/latest_version_oracle.py --json-out /tmp/latest_oracle.json
```

`CONTAINER_RUNTIME=apptainer|docker` forces the runtime instead of auto-detecting; `JOBS` (default 4)
controls parallelism. A single case/condition/rep can still be reproduced directly with
`benchmark/run_case_opencode_deepseek.sh` (see its usage comment). `analyze_top_opencode.py` expects
both output sets merged into one directory (same case/condition/run-N layout, disjoint case IDs so a
straight `rsync`/symlink merge works).
