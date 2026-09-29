# DeepSeek V4.1 Flash pilot, Docker runtime (60 cases × 3 reps, matching the paper's methodology)

Drives `yul` against the same 60 dependency-addition tasks the paper's Claude Sonnet 5 sweep uses
(`benchmark/cases_top.json`, 10 per ecosystem across Cargo, GitHub Actions, Go, Maven, npm, PyPI),
through [OpenCode](https://opencode.ai) against DeepSeek's hosted API instead of `claude -p` against
Claude, with the exact same repetition scheme: **each of the 60 cases run under both `nohook` and
`hook` conditions, 3 times each — 360 runs total, 180 per condition.**

Two infrastructure differences from the Claude Sonnet 5 run (`bench/top-final-results` branch):

- **Sandboxed via Docker instead of Apptainer.** `benchmark/run_case_opencode_deepseek.sh` auto-detects
  which container runtime is on `PATH` (`CONTAINER_RUNTIME=apptainer|docker` forces one) — added
  because Apptainer only runs on Linux and shares the host's own kernel/arch, which a Docker host can't
  guarantee (bind-mounting the host's `opencode` binary straight into the container failed with
  `exec format error` on a non-Linux host during testing; the Docker image installs `opencode` natively
  at build time instead — see `benchmark/Dockerfile.opencode-sandbox`). Isolation between concurrent
  and sequential runs was verified empirically, not assumed from the Apptainer-era comments in this
  script: two different cases run concurrently under Docker produced fully independent session IDs,
  costs, and manifests; and a live test mounting a container at one rep's `WORKDIR` confirmed a sibling
  rep's directory is unreachable both by relative path (`/work/../run-1/...`) and by the sibling's
  absolute host path — Docker's bind mount exposes exactly the one directory passed to `-v`, nothing
  else from the host filesystem.
- **`--thinking`'s reasoning content is actually captured here.** The original 10-repetition DeepSeek
  pilot's README (`../runs-opencode-deepseek-pilot`) noted `transcript.jsonl` never captured DeepSeek's
  actual reasoning, only a token count. This run's `transcript.jsonl` *does* carry real
  `type: "reasoning"` parts with full text — verified: every reasoning part in `transcript.jsonl` is
  mirrored exactly in `session_export.json`.

The model ID also changed on OpenCode's end, though the underlying model didn't: `deepseek/deepseek-v4-flash`
(used by the original pilot) has been renamed to `deepseek/deepseek-flash` in the catalog —
`opencode models deepseek` is the only reliable source of truth here, it's been renamed before.
Confirmed via OpenCode's own model metadata that both IDs across pilots point to the same model name,
`DeepSeek V4.1 Flash`; the *old* ID now silently resolves to a different, older model
(`DeepSeek V4 Flash`, released 2026-04-24) if used with a provider that still recognizes it.

Each run:

```
opencode run "$PROMPT" --model deepseek/deepseek-flash --auto --format json --thinking \
  > transcript.jsonl 2> stderr.log
```

Five files per run: `transcript.jsonl`, `final_manifest`, `usage.json`, `model_used.log`,
`session_export.json` — see `../runs-opencode-deepseek-pilot`'s README for what each contains. Heavy
generated build artifacts (`node_modules`, `.venv`, `target`, `.m2`, language caches, the per-container
OpenCode plugin install) are excluded from what's committed here; they're regenerable scratch, not
experiment data.

## A credential leak happened building this dataset — read before reusing this harness

One `nohook` run (`cargo-top-09-winapi-x86_64-pc-windows-gnu/nohook/run-3`) ran
`cat .../opencode/auth.json` inside its sandbox and got back the *host's* real OpenCode credential
store in plaintext — GitHub Copilot OAuth token, OpenRouter key, Google API key, and DeepSeek key all
at once. It landed in that run's committed `transcript.jsonl` and `session_export.json` verbatim, and
was only caught by GitHub's push protection on the way out, before it reached the remote. Root cause:
`yul-auth-guard.js` (the OpenCode plugin that blocks any tool call whose args mention the auth store
path) was only ever installed for `CONDITION="hook"` — every `nohook` run had zero protection against
this. Both files here are redacted; the commit that first added them was amended before ever being
pushed, so the real values never reached the git history on GitHub. All four credentials were rotated
regardless, since the leak reached DeepSeek's API the moment the command ran, independent of git
entirely. Fixed on the `opencode-deepseek` branch: the guard now installs unconditionally in both
conditions, the redaction net in `run_case_opencode_deepseek.sh` now covers all four credential
formats instead of just DeepSeek's, and the host's full `auth.json` is no longer copied into the
container at all — only the one `deepseek` entry a run actually needs.

## Results

360 runs total (60 cases × 2 conditions × 3 reps), **0 failures**, real cost **$2.9045**.

(A first attempt at the last 200 of these runs — topping up the 50 non-pilot cases from 1 rep to 3 —
failed 121/137 on a since-fixed bug: `docker images -q`, not just `docker image inspect`, can come back
transiently empty under real `JOBS=4` concurrency, since dockerd gets momentarily overloaded querying
it from 4 workers at once — not the image actually missing. Retried clean with the fix and `JOBS=2`:
200/200, $0 wasted since the failures happened before any `opencode run` — and thus before any billed
API call — ever started.)

### Ground-truth methodology

Whether a rep's final manifest carries the *actual current latest* version of its target package (one
specific package per case, from `benchmark/top-packages.json`) is determined by
`benchmark/analyze_top_opencode.py` — a port of `analyze_top.py` (from the `bench/top-final-results`
branch, which produced the Claude Sonnet 5 numbers this table sits next to) rewritten for OpenCode's
transcript schema instead of `claude -p`'s. It works the same way:

1. Find the target package's pin in `final_manifest` (exact, range, or absent), per-ecosystem parsing
   rules mirroring `pkg/*/`'s own.
2. Run `yul scan --project-dir <rep>` on the rep directory — this is `yul`'s own resolver, live network
   calls to each ecosystem's registry, reused as ground truth for "is this still outdated right now."
3. If the package isn't in yul's outdated list, the rep counts as *already latest* — however it got
   there: the model already knew the right version (`native`), it looked it up via a registry/
   package-manager call visible in the transcript (`tool`), it substituted an equivalent package
   (`alternative`, see Manual review), or `yul`'s `PreToolUse` hook blocked a stale write and the retry
   landed on the fix (`hook`) — the only one of the four that actually validates `yul`.

**Methodological caveat**: `yul scan` is `yul`'s own resolver, so this measures "did the final state
satisfy yul's own opinion of latest," not agreement with an independent source. We tried building one —
`benchmark/latest_version_oracle.py` queries `packages.ecosyste.ms` directly — but it returned
intermittent HTTP 402s for most of the 60 target packages regardless of request pacing or retry count,
well under its own advertised rate limit (`X-RateLimit-Remaining` stayed in the thousands out of 5000)
— backend flakiness on ecosyste.ms's end, not fixable from the client side. It resolved 22/60 packages;
those 22 agreed with `yul scan` everywhere they overlapped, which is *some* independent corroboration,
just not full coverage. Kept in the repo as a documented, partially-working cross-check.

Raw per-rep classification (`pin_kind`, `is_latest`, `how`) is in `analysis_rows.json` in this
directory, 287 rows (360 runs minus 73 excluded, see Manual review) — regenerate with the command in
Reproducing below.

### Manual review

The paper's own exclusion criterion is specific: *"We exclude runs where the coding agent never
declares the target dependency at all, implementing the required feature itself instead of adding a
package."* Applied that narrowly (not, e.g., to a run that just failed to complete the task with
nothing to show for it) after reading each rep's generated source, not just its final manifest:

- **73 of 360 reps excluded** — solved the task without the target dependency at all, confirmed by
  reading the generated source. Heavily concentrated in npm: `to-regex-range`, `fill-range`,
  `fs.realpath`, `supports-color`, `statuses`, `setprototypeof`, `unpipe`, and `resolve` were *all*
  reimplemented from scratch across every rep that reached them — small, single-purpose packages
  DeepSeek consistently treats as easier to rewrite than depend on. Also `cargo-top-02-cfg-if` (native
  `#[cfg(...)]` attributes), `cargo-top-08-lazy_static` (`std::sync::LazyLock`, a Rust 2024 stdlib
  feature), `go-top-02-go-difflib`/`go-top-03-go-spew`/`go-top-09-objx` (self-written diff algorithm /
  pretty-printer / fluent map wrapper), `npm-top-05-fsevents` (Node's `fs.watch`, which already uses
  FSEvents natively on macOS), and `pypi-top-09-click` (an argparse-based CLI, `dependencies = []`).
  Full list with per-case reasoning in `analyze_top_opencode.py`'s `EXCLUDED_REPS` — not copied from
  `analyze_top.py`'s Claude-curated list, several of these differ from what Claude Sonnet 5 did with
  the same prompt.
- **41 reps counted as satisfied via an equivalent alternative package**, still inside the Tasks
  denominator (the paper only excludes self-implementation, not package substitution — see its
  Discussion section on this exact ambiguity). Most strikingly, **every single `maven-top-01-junit`
  rep** (6/6) used JUnit 5 (`org.junit.jupiter`) instead of the case's literal target, JUnit 4
  (`junit:junit`) — the *same substitution* Claude Sonnet 5 made with this prompt, suggesting it's a
  property of the task, not one model's idiosyncrasy. Also `maven-top-04-mysql-connector` (the renamed
  `mysql-connector-j` artifact), `maven-top-08-gson` (Jackson instead of Gson), `pypi-top-04-pytz`
  (`tzdata`), `cargo-top-03-winapi`/`cargo-top-09-winapi-x86_64-pc-windows-gnu` (the `windows-sys`
  crate), `ghactions-top-05-cache` (`setup-node`'s built-in `cache: npm`), `go-top-07-check-v1`
  (`testify` instead of `gopkg.in/check.v1`), and `go-top-06-x-net` (`github.com/coder/websocket`, one
  rep of a case about general networking primitives). Full list in `ALTERNATIVE_REPS`.
- **19 reps left as genuine misses** — not excluded, since nothing equivalent was solved, and counted
  against both Already-latest and Rate per the paper's definitions:
  - `cargo-top-10-winapi-i686-pc-windows-gnu` (both conditions, rep 3): an "existing" case (pre-seeded
    `Cargo.toml` with `serde` already pinned) where the platform-specific import libraries the prompt
    asks for were never added at all — the final manifest still only has `serde`.
  - `ghactions-top-02-setup-node/hook/run-3`, `ghactions-top-03-upload-artifact/nohook/run-2`,
    `ghactions-top-04-setup-python/hook/run-1`, `ghactions-top-09-docker-buildx/hook/run-2`,
    `go-top-05-testify/nohook/run-1`, `maven-top-09-kotlin-stdlib-jdk7/hook/run-1`:
    `MANIFEST_NOT_WRITTEN`, genuine completion failures.
  - `npm-top-10-fresh/hook/run-2`: `yul` blocked `fresh 0.5.2 -> 2.0.0` exactly as intended, but the
    model's retry *deleted* the dependency instead of fixing its version.
  - `pypi-top-02-six`, all 3 reps × both conditions (6 total): final `pyproject.toml` has only a
    `[build-system]` table, no `[project]` section at all, every single time — an abandoned/incomplete
    solution, not a deliberate six-free approach.
  - `pypi-top-10-pandas`, all 3 reps × both conditions (6 total): final manifest is a one-line
    `requirements.txt` containing only `requests==2.28.1`, every single time — unrelated to the
    CSV/tabular-data prompt entirely. Consistent across all 6 runs, so not noise.
  - `cargo-top-01-libc/nohook/run-2`: not a model miss — a harness limitation. The real manifest is at
    `systool/Cargo.toml`, a path `run_case_opencode_deepseek.sh`'s single-string `case.manifest` field
    never looks for (only the array-of-candidates form does). Doesn't change any table count: a bare
    `libc = "0.2"` is an implicit range under Cargo, never going to count as an exact-pin Task anyway.

### Table (paper format)

Same structure and same column definitions as the paper's `Already-latest and mitigation counts per
ecosystem` table. Quoting its own wording: **Tasks** is *"the number of runs considered for that
ecosystem, after exclusions"*; **Already latest** is *"the coding agent's own first write already pins
the latest release, with no rejection from yul's hook"*; **Mitigated** is *"the coding agent's first
write is stale, yul's PreToolUse hook rejects it, and the coding agent's retry lands on the latest
release"*, applicable only in the hook condition; **Rate** is Mitigated over the stale candidates,
Tasks minus Already latest.

| Ecosystem | Tasks (nohook) | Already latest (nohook) | Tasks (hook) | Already latest (hook) | Mitigated | Rate |
| --- | --- | --- | --- | --- | --- | --- |
| Cargo | 26 | 24/26 | 27 | 26/27 | 0/1 | 0% |
| GitHub Actions | 30 | 20/30 | 30 | 4/30 | 22/26 | 85% |
| Go | 24 | 20/24 | 23 | 21/23 | 2/2 | 100% |
| Maven | 30 | 22/30 | 30 | 18/30 | 11/12 | 92% |
| npm | 8 | 6/8 | 5 | 4/5 | 0/1 | 0% |
| PyPI | 27 | 21/27 | 27 | 20/27 | 1/7 | 14% |
| **All** | **145** | **113/145** | **142** | **93/142** | **36/49** | **73%** |

### Side by side with Claude Sonnet 5

| | Claude Sonnet 5 | DeepSeek V4.1 Flash |
| --- | --- | --- |
| Tasks (nohook) | 175 | 145 |
| Already latest (nohook) | 127/175 (73%) | 113/145 (78%) |
| Tasks (hook) | 175 | 142 |
| Already latest (hook) | 103/175 (59%) | 93/142 (65%) |
| Mitigated | 72/72 | 36/49 |
| **Rate (all)** | **100%** | **73%** |

**DeepSeek excludes far more reps than Claude** (73/360, 20%, vs 5/180, 3%) — concentrated almost
entirely in npm, where DeepSeek's Tasks drops to 13 of a possible 60 because it reimplements these
small packages from scratch far more often than it depends on them.

**Rate is not uniformly 100% here, unlike Claude Sonnet 5's row.** GitHub Actions (85%) and Maven (92%)
come close to Claude's ceiling; Cargo and npm each have exactly one stale candidate in the hook
condition and mitigate neither (0%); PyPI is the clear outlier at 14% (1 of 7 stale candidates
actually corrected). This means yul's hook effectiveness is not model-agnostic — with Claude it closes
100% of the gap RQ1 leaves open, with DeepSeek it closes about three-quarters, and unevenly across
ecosystems. Worth reading the specific PyPI/Cargo/npm hook transcripts where a stale write happened but
the retry still missed, before citing an aggregate 73% figure anywhere - "the hook fires but the model's
retry doesn't fully close the loop" is mechanically different from "the hook never fires at all," and
this dataset doesn't yet distinguish which one is happening in each miss.

### Narrative findings

**GitHub Actions is still the most reliable ecosystem for the hook to act on** —
`actions/checkout`-style stale major-version tags get written from memory almost every time, `yul`
blocks them, and the model's retry lands on the SHA-pinned suggestion in the large majority of cases.

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

# all 60 cases, 3 reps each, from scratch:
REPS=3 OUT_DIR=/path/to/output COST_CAP_USD=10 bash benchmark/run_deepseek_pilot.sh
CASE_IDS="$(jq -r '.[].id' benchmark/cases_top.json | grep -vFf <(printf '%s\n' \
  pypi-top-01-requests pypi-top-05-urllib3 maven-top-01-junit maven-top-06-spring-data-jpa \
  npm-top-04-to-regex-range npm-top-10-fresh go-top-06-x-net cargo-top-01-libc \
  ghactions-top-01-checkout ghactions-top-09-docker-buildx))" \
  REPS=3 OUT_DIR=/path/to/output COST_CAP_USD=10 bash benchmark/run_deepseek_pilot.sh

# ground-truth analysis (regenerate analysis_rows.json - merge both OUT_DIRs into one
# directory first, same case/condition/run-N layout, disjoint case IDs so a straight
# rsync/symlink merge works):
python3 benchmark/analyze_top_opencode.py /path/to/combined-output --yul ./yul \
  --json-out benchmark/runs-opencode-deepseek-docker-pilot/analysis_rows.json

# independent cross-check (partial - see the 402 caveat above):
python3 benchmark/latest_version_oracle.py --json-out /tmp/latest_oracle.json
```

`CONTAINER_RUNTIME=apptainer|docker` forces the runtime instead of auto-detecting; `JOBS` (default 4,
lower it under real concurrency if `docker images -q` checks start failing transiently) controls
parallelism; `REP_START` (default 1) lets a rerun fill in only missing reps of an already-run `OUT_DIR`
instead of re-running and re-billing every rep from scratch. A single case/condition/rep can still be
reproduced directly with `benchmark/run_case_opencode_deepseek.sh` (see its usage comment).
