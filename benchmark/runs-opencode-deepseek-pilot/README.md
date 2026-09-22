# DeepSeek-V4.1-Flash pilot (10 cases × 10 repetitions)

Same idea as [`benchmark/top`](https://github.com/chains-project/yul/tree/main/benchmark/top) (`yul`
against real dependency-addition tasks, once with the hook installed and once without), but driven
through [OpenCode](https://opencode.ai) instead of `claude -p`, against DeepSeek's hosted API
(`deepseek/deepseek-v4-flash`) instead of Claude, and with **each case/condition repeated 10 times**
instead of once — to see how much of the block/self-correction behavior is consistent versus
per-run variance.

Each run:

```
opencode run "$PROMPT" --model deepseek/deepseek-v4-flash --auto --format json \
  > transcript.jsonl 2> stderr.log
```

Four files come out of each run (`benchmark/run_case_opencode_deepseek.sh`):

- `transcript.jsonl` — full turn-by-turn record (every message, tool call, and tool result,
  including any `yul` block), one JSON object per line. Doesn't record which model/provider served
  the request (see `model_used.log`).
- `final_manifest` — a copy of whatever manifest file (`pom.xml`, `requirements.txt`, etc.) exists
  on disk once OpenCode finishes.
- `usage.json` — per-run token counts and **real dollar cost**, aggregated from the transcript's
  `step_finish` events (DeepSeek is a priced API, unlike the self-hosted Qwen runs in
  `../runs-opencode-qwen-60/`, where `cost_usd` was always `0`).
- `model_used.log` — the `providerID=deepseek modelID=deepseek-v4-flash` lines pulled from
  OpenCode's own runtime log (`~/.local/share/opencode/log/opencode.log`) for this run's session ID —
  direct proof of which model actually served it, since the transcript itself never says.

10 cases were picked from the full 60-case set (`benchmark/cases_top.json`), weighted toward Maven
and GitHub Actions since those showed the highest block rates in the earlier 60-case Qwen sweep
(`../runs-opencode-qwen-60/SUMMARY.md`): `pypi-top-01-requests`, `pypi-top-05-urllib3`,
`maven-top-01-junit`, `maven-top-06-spring-data-jpa`, `npm-top-04-to-regex-range`,
`npm-top-10-fresh`, `go-top-06-x-net`, `cargo-top-01-libc`, `ghactions-top-01-checkout`,
`ghactions-top-09-docker-buildx`.

## Results

200 runs total (10 cases × 2 conditions × 10 reps), **0 failures**, real cost **$1.1444**.

| Case | Ecosystem | Blocked (hook) | Corrected to suggested | Cost (hook, ×10) | Cost (nohook, ×10) |
| --- | --- | --- | --- | --- | --- |
| `pypi-top-01-requests` | PyPI | 0/10 | n/a | $0.0640 | $0.0628 |
| `pypi-top-05-urllib3` | PyPI | 1/10 | 0/1 | $0.0678 | $0.0851 |
| `maven-top-01-junit` | Maven | 7/10 | 16/16 | $0.0604 | $0.0496 |
| `maven-top-06-spring-data-jpa` | Maven | 2/10 | 2/2 | $0.1775 | $0.1077 |
| `npm-top-04-to-regex-range` | npm | 0/10 | n/a | $0.0522 | $0.0846 |
| `npm-top-10-fresh` | npm | 7/10 | 5/7 | $0.0410 | $0.0135 |
| `go-top-06-x-net` | Go modules | 0/10 | n/a | $0.0363 | $0.0437 |
| `cargo-top-01-libc` | Cargo | 0/10 | n/a | $0.0494 | $0.0434 |
| `ghactions-top-01-checkout` | GitHub Actions | 10/10 | 10/10 | $0.0261 | $0.0139 |
| `ghactions-top-09-docker-buildx` | GitHub Actions | 10/10 | 59/59 | $0.0400 | $0.0257 |
| **Total** | | **37/100** | **92/94** | **$0.5147** | **$0.5300** |

"Blocked" is how many of the 10 hook repetitions triggered at least one real `yul` block (the
`outdated dependencies, use these versions instead:` message, not a heuristic match). "Corrected to
suggested" is, across every (dependency, flagged-version) pair `yul` flagged in those blocked runs,
how many ended with `yul`'s exact suggested version landing in the final manifest.

## What the repetition shows

**GitHub Actions blocked 10/10, every time, both cases.** DeepSeek reliably writes stale
`actions/checkout@v4`-style tags on the first attempt, `yul` reliably catches it, and DeepSeek
reliably retries with the corrected pin — no run escaped the block, and every flagged action
(`ghactions-top-09-docker-buildx` alone flags 4 different actions per run) ended up corrected. This
matches the 9/10 GitHub Actions block rate from the full 60-case Qwen sweep — the pattern isn't
specific to Qwen.

**Maven and npm-fresh are stochastic, not deterministic.** `maven-top-01-junit` blocked in 7 of 10
reps and `npm-top-10-fresh` in 7 of 10 — the other ~30% of reps, DeepSeek happened to land on a
version that either matched a property placeholder (`${junit.version}`) or was already current on
that particular sample, so there was nothing to block. `maven-top-06-spring-data-jpa` blocked far
less often (2/10) — its only exactly-pinned dependency is `spring-boot-starter-parent`, and DeepSeek
mostly wrote it via a property or left it to the parent POM to resolve, so it rarely produces an
exact stale pin at all.

**PyPI, npm-to-regex-range, Go, and Cargo essentially never blocked**, same as the larger Qwen
sweep and for the same reason: DeepSeek prefers ranges (`requests>=2.20`, `^5.0.1`) or shells out to
the ecosystem's own installer (`go get`, `cargo add`) rather than hand-writing an exact pin — neither
of which `yul`'s `Write`/`Edit`-only check (or the OpenCode plugin's bash heuristic) has anything to
catch, since there's no exact version being written in the first place. `pypi-top-05-urllib3` blocked
exactly once in 10 tries — the one rep where DeepSeek happened to write `urllib3==2.8.0` instead of a
range.

**Scaffolding details vary far more than dependency handling.** Across repetitions, the *project
name*, *module path*, and *file layout* changed run to run (`sys-tool` vs `systems-tool` vs
`sys_tool` for the same Cargo case; `example.com/netapp` vs `netapp` vs `github.com/example/netapp`
for the same Go case) — but the dependency-version behavior for a given case was much more
consistent, which is what makes the block-rate numbers above meaningful rather than noise.

**Real cost stayed low.** DeepSeek's automatic context caching kicked in on all 200/200 runs
(`cache_read` > 0 in every `usage.json`) — the $1.1444 total for 200 runs came in well under the
$3.10 estimate projected from the Qwen sweep's token counts before this pilot ran.

## Reproducing

```sh
export DEEPSEEK_API_KEY=...   # or source .env
go build -o yul .
bash benchmark/run_case_opencode_deepseek.sh benchmark/cases_top.json <case_id> <hook|nohook> \
  benchmark/runs-opencode-deepseek-pilot deepseek/deepseek-v4-flash <repeat_index>
```
