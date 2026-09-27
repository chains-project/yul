# DeepSeek V4.1 Flash pilot, Docker runtime (10 cases × 3 repetitions)

Same 10-case subset and idea as [`../runs-opencode-deepseek-pilot`](../runs-opencode-deepseek-pilot)
(`yul` against real dependency-addition tasks, once with the hook installed and once without, driven
through [OpenCode](https://opencode.ai) against DeepSeek's hosted API), but two things changed:

- **Sandboxed via Docker instead of Apptainer.** `benchmark/run_case_opencode_deepseek.sh` now
  auto-detects which container runtime is on `PATH` (`CONTAINER_RUNTIME=apptainer|docker` forces
  one) — added because Apptainer only runs on Linux and shares the host's own kernel/arch, which a
  Docker host can't guarantee (bind-mounting the host's `opencode` binary straight into the
  container failed with `exec format error` on a non-Linux host during testing; the Docker image now
  installs `opencode` natively at build time instead — see `benchmark/Dockerfile.opencode-sandbox`).
  Verified this doesn't change the isolation properties that matter: two different cases run
  concurrently under Docker produced fully independent session IDs, costs, and manifests, same as
  the Apptainer path already guaranteed.
- **Only 3 repetitions instead of 10** (60 runs total instead of 200), orchestrated by the new
  `benchmark/run_deepseek_pilot.sh` (fan-out via `xargs -P`, plus a watchdog that polls real
  `usage.json` cost every 15s and kills the whole run if `COST_CAP_USD` is crossed) instead of ad
  hoc shell.

The model ID also changed on OpenCode's end, though the underlying model didn't:
`deepseek/deepseek-v4-flash` (used by the original pilot) has been renamed to `deepseek/deepseek-flash`
in the catalog — `opencode models deepseek` is the only reliable source of truth here, it's been
renamed before. Confirmed via OpenCode's own model metadata that both IDs across pilots point to the
same model name, `DeepSeek V4.1 Flash`; the *old* ID now silently resolves to a different, older
model (`DeepSeek V4 Flash`, released 2026-04-24) if used with a provider that still recognizes it, so
don't reuse it by habit.

One capture gap from the original pilot is also fixed here: that pilot's README noted
`transcript.jsonl` never captured DeepSeek's actual reasoning content, only a token count. This run's
`transcript.jsonl` *does* carry real `type: "reasoning"` parts with full text (OpenCode's `--thinking`
flag, already used by `run_case_opencode_deepseek.sh`, works correctly under both runtimes) —
verified: every reasoning part in `transcript.jsonl` is mirrored exactly in `session_export.json`.

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

60 runs total (10 cases × 2 conditions × 3 reps), **0 failures**, real cost **$0.4000**.

| Case | Ecosystem | Blocked (hook) | Corrected to suggested | Cost (hook, ×3) | Cost (nohook, ×3) |
| --- | --- | --- | --- | --- | --- |
| `pypi-top-01-requests` | PyPI | 1/3 | 1/1 | $0.0413 | $0.0162 |
| `pypi-top-05-urllib3` | PyPI | 1/3 | 3/3 | $0.0268 | $0.0170 |
| `maven-top-01-junit` | Maven | 3/3 | 6/6 | $0.0161 | $0.0111 |
| `maven-top-06-spring-data-jpa` | Maven | 1/3 | 1/1 | $0.0328 | $0.0136 |
| `npm-top-04-to-regex-range` | npm | 0/3 | n/a | $0.0329 | $0.0255 |
| `npm-top-10-fresh` | npm | 1/3 | 0/1 | $0.0092 | $0.0016 |
| `go-top-06-x-net` | Go modules | 0/3 | n/a | $0.0238 | $0.0113 |
| `cargo-top-01-libc` | Cargo | 0/3 | n/a | $0.0508 | $0.0494 |
| `ghactions-top-01-checkout` | GitHub Actions | 3/3 | 5/5 | $0.0077 | $0.0017 |
| `ghactions-top-09-docker-buildx` | GitHub Actions | 3/3 | 12/18 | $0.0068 | $0.0045 |
| **Total** | | **13/30** | **28/35** | **$0.2481** | **$0.1519** |

"Blocked" and "Corrected to suggested" are computed the same way as the original pilot: a hook rep
counts as blocked if `yul` rejected at least one write with the real
`outdated dependencies, use these versions instead:` message; "corrected" counts each distinct
(dependency, suggested-version) pair `yul` flagged across those blocked reps against whether that
exact suggested version string ended up in the run's `final_manifest`.

## What this run shows

**GitHub Actions is still perfectly reliable — 3/3 blocked, every flagged action eventually
corrected.** Matches both the original 60-case Qwen sweep and the 10-repetition DeepSeek pilot: the
model writes a stale `actions/checkout@v4`-style tag from memory, `yul` blocks it, and the retry lands
on the SHA-pinned suggestion every time.

**Maven is still split between the two cases for the same reason as before.** `maven-top-01-junit`
blocked 3/3 (its dependencies are always exact pins); `maven-top-06-spring-data-jpa` blocked only 1/3,
because its one exactly-pinnable dependency, `spring-boot-starter-parent`, gets written as a property
or resolved through the parent POM in the other two reps instead of a literal version string yul can
see.

**PyPI, npm, Go, and Cargo still rarely produce an exact pin to block**, same root cause as before:
the model prefers ranges (`>=`, `^`) or shells out to the ecosystem's own installer (`go get`,
`cargo add`) rather than hand-writing a version — neither is visible to a `Write`/`Edit`-only hook.
When PyPI *did* produce an exact pin, `yul` corrected it 100% of the time (4/4 across both cases).

**A new failure mode showed up in `npm-top-10-fresh` rep 2**: `yul` blocked `fresh 0.5.2 -> 2.0.0` as
expected, but instead of writing the corrected version, the model's retry dropped the `fresh`
dependency from `package.json` entirely. Different from the original pilot's blocked-but-uncorrected
cases (which were near-misses on the version string) — here the model resolved the block by removing
the thing being blocked, a real behavior worth watching for at larger scale.

**The sandbox image (Apptainer and Docker both) has no per-ecosystem toolchains baked in** — only
`ca-certificates curl git jq nodejs npm python3`. Every Maven/Go/Cargo run has to self-bootstrap its
own JDK/Maven/Go/Rust from the internet inside the fresh, throwaway container, which is real
per-run latency and (soon-evicted) cache churn that PyPI/npm/GitHub-Actions cases don't pay. Caught
live in `maven-top-06-spring-data-jpa/hook/run-3`: the model downloaded JDK 17 and Maven 3.9.9
tarballs by hand, then ran Maven with an apparently-unresolved shell variable as
`-Dmaven.repo.local`, which silently wrote its ~90MB local repository cache into a directory
literally named `?` inside the workdir (excluded from what's committed here, along with all other
build caches). Worth deciding later whether to bake these toolchains into the sandbox image the same
way `opencode` now is for Docker.

## Reproducing

```sh
go build -o yul .
docker build -t yul-opencode-sandbox -f benchmark/Dockerfile.opencode-sandbox benchmark/
# or: apptainer build benchmark/opencode-sandbox.sif benchmark/opencode-sandbox.def
opencode auth login -p deepseek   # credential lives in OpenCode's own store, never an env var

REPS=3 OUT_DIR=/path/to/output COST_CAP_USD=10 bash benchmark/run_deepseek_pilot.sh
```

`CONTAINER_RUNTIME=apptainer|docker` forces the runtime instead of auto-detecting; `JOBS` (default 4)
controls parallelism. A single case/condition/rep can still be reproduced directly with
`benchmark/run_case_opencode_deepseek.sh` (see its usage comment).
