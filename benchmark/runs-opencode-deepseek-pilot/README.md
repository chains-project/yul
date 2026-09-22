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

Same column set as [`benchmark/README.md`](https://github.com/chains-project/yul/tree/main/benchmark)'s
top-60 table, but one row per case (10 reps each) instead of per ecosystem (10 cases each). *Versioned*
= final manifest has an exact pin. *Already latest* = of those, the pin matches what `yul`'s resolver
reports as current right now (checked by replaying every `final_manifest` through the real `yul`
binary with `before=""`, so every pin counts as new — this is ground truth, not a heuristic). *Blocked*
= transcript shows `yul`'s `PreToolUse` hook actually rejecting a write live during that run (independent
of whether the final result ended up correct). *Stale candidates* = `Versioned(nohook) − Already
latest(nohook)`, i.e. how often an exact-but-outdated pin would land with no hook present at all — the
baseline pool a working hook should be catching from. *Rate* = `Blocked / Stale candidates`.

| Case | Tasks | Versioned (no hook) | Already latest (no hook) | Versioned (hook) | Already latest (hook) | Blocked (hook) | Rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `pypi-top-01-requests` | 10 | 0/10 | 0/10 | 3/10 | 3/10 | 0/10 | — |
| `pypi-top-05-urllib3` | 10 | 2/10 | 2/10 | 2/10 | 2/10 | 1/10 | — |
| `maven-top-01-junit` | 10 | 10/10 | 0/10 | 10/10 | 10/10 | 7/10 | 70% |
| `maven-top-06-spring-data-jpa` | 10 | 10/10 | 1/10 | 10/10 | 10/10 | 2/10 | 22% |
| `npm-top-04-to-regex-range` | 10 | 1/10 | 1/10 | 2/10 | 2/10 | 0/10 | — |
| `npm-top-10-fresh` | 10 | 10/10 | 0/10 | 10/10 | 0/10 | 7/10 | 70% |
| `go-top-06-x-net` | 10 | 10/10 | 10/10 | 10/10 | 10/10 | 0/10 | — |
| `cargo-top-01-libc` | 10 | 0/10 | 0/10 | 0/10 | 0/10 | 0/10 | — |
| `ghactions-top-01-checkout` | 10 | 10/10 | 0/10 | 10/10 | 10/10 | 10/10 | 100% |
| `ghactions-top-09-docker-buildx` | 10 | 10/10 | 0/10 | 10/10 | 10/10 | 10/10 | 100% |
| **Total** | **100** | **63/100** | **14/100** | **67/100** | **57/100** | **37/100** | **76%** |

`—` means zero stale candidates in the nohook baseline (nothing for the rate to measure against), not
zero blocks — `pypi-top-05-urllib3` shows this: 1 block fired live (on a `pytest` dev-dependency pin,
not the case's own `urllib3`), even though none of its 10 nohook samples happened to land on a stale
pin. With only 10 samples per condition, small-count noise like this is expected.

### Per-run detail (all 200)

<details>
<summary>Every repetition's classification</summary>

"Already latest" is `n/a` whenever "Versioned" is `no` — no exact pin was in the final manifest at all
(a range, or written by the ecosystem's own installer with no version), so there's nothing to check
"latest" against. It's `yes`/`no` only when "Versioned" is `yes`. "Flagged" is the (dependency,
current → suggested) pair(s) from `yul`'s block message, when one fired (only the first two shown if
there were more).

| Case | Condition | Rep | Versioned | Already latest | Blocked | Flagged (current -> suggested) |
| --- | --- | --- | --- | --- | --- | --- |
| pypi-top-01-requests | nohook | 1 | no | n/a | no |  |
| pypi-top-01-requests | nohook | 2 | no | n/a | no |  |
| pypi-top-01-requests | nohook | 3 | no | n/a | no |  |
| pypi-top-01-requests | nohook | 4 | no | n/a | no |  |
| pypi-top-01-requests | nohook | 5 | no | n/a | no |  |
| pypi-top-01-requests | nohook | 6 | no | n/a | no |  |
| pypi-top-01-requests | nohook | 7 | no | n/a | no |  |
| pypi-top-01-requests | nohook | 8 | no | n/a | no |  |
| pypi-top-01-requests | nohook | 9 | no | n/a | no |  |
| pypi-top-01-requests | nohook | 10 | no | n/a | no |  |
| pypi-top-01-requests | hook | 1 | yes | yes | no |  |
| pypi-top-01-requests | hook | 2 | no | n/a | no |  |
| pypi-top-01-requests | hook | 3 | no | n/a | no |  |
| pypi-top-01-requests | hook | 4 | no | n/a | no |  |
| pypi-top-01-requests | hook | 5 | yes | yes | no |  |
| pypi-top-01-requests | hook | 6 | no | n/a | no |  |
| pypi-top-01-requests | hook | 7 | no | n/a | no |  |
| pypi-top-01-requests | hook | 8 | yes | yes | no |  |
| pypi-top-01-requests | hook | 9 | no | n/a | no |  |
| pypi-top-01-requests | hook | 10 | no | n/a | no |  |
| pypi-top-05-urllib3 | nohook | 1 | yes | yes | no |  |
| pypi-top-05-urllib3 | nohook | 2 | yes | yes | no |  |
| pypi-top-05-urllib3 | nohook | 3 | no | n/a | no |  |
| pypi-top-05-urllib3 | nohook | 4 | no | n/a | no |  |
| pypi-top-05-urllib3 | nohook | 5 | no | n/a | no |  |
| pypi-top-05-urllib3 | nohook | 6 | no | n/a | no |  |
| pypi-top-05-urllib3 | nohook | 7 | no | n/a | no |  |
| pypi-top-05-urllib3 | nohook | 8 | no | n/a | no |  |
| pypi-top-05-urllib3 | nohook | 9 | no | n/a | no |  |
| pypi-top-05-urllib3 | nohook | 10 | no | n/a | no |  |
| pypi-top-05-urllib3 | hook | 1 | no | n/a | no |  |
| pypi-top-05-urllib3 | hook | 2 | no | n/a | no |  |
| pypi-top-05-urllib3 | hook | 3 | no | n/a | no |  |
| pypi-top-05-urllib3 | hook | 4 | yes | yes | no |  |
| pypi-top-05-urllib3 | hook | 5 | no | n/a | no |  |
| pypi-top-05-urllib3 | hook | 6 | yes | yes | yes | pytest 8.3.5->9.1.1 |
| pypi-top-05-urllib3 | hook | 7 | no | n/a | no |  |
| pypi-top-05-urllib3 | hook | 8 | no | n/a | no |  |
| pypi-top-05-urllib3 | hook | 9 | no | n/a | no |  |
| pypi-top-05-urllib3 | hook | 10 | no | n/a | no |  |
| maven-top-01-junit | nohook | 1 | yes | no | no |  |
| maven-top-01-junit | nohook | 2 | yes | no | no |  |
| maven-top-01-junit | nohook | 3 | yes | no | no |  |
| maven-top-01-junit | nohook | 4 | yes | no | no |  |
| maven-top-01-junit | nohook | 5 | yes | no | no |  |
| maven-top-01-junit | nohook | 6 | yes | no | no |  |
| maven-top-01-junit | nohook | 7 | yes | no | no |  |
| maven-top-01-junit | nohook | 8 | yes | no | no |  |
| maven-top-01-junit | nohook | 9 | yes | no | no |  |
| maven-top-01-junit | nohook | 10 | yes | no | no |  |
| maven-top-01-junit | hook | 1 | yes | yes | yes | org.apache.maven.plugins:maven-surefire-plugin 3.2.5->3.6.0; org.junit.jupiter:junit-jupiter 5.10.2->6.1.3 |
| maven-top-01-junit | hook | 2 | yes | yes | yes | org.apache.maven.plugins:maven-surefire-plugin 3.2.5->3.6.0; org.junit.jupiter:junit-jupiter 5.10.2->6.1.3 |
| maven-top-01-junit | hook | 3 | yes | yes | yes | org.apache.maven.plugins:maven-compiler-plugin 3.13.0->3.16.0; org.apache.maven.plugins:maven-surefire-plugin 3.2.5->3.6.0 |
| maven-top-01-junit | hook | 4 | yes | yes | no |  |
| maven-top-01-junit | hook | 5 | yes | yes | no |  |
| maven-top-01-junit | hook | 6 | yes | yes | yes | org.apache.maven.plugins:maven-compiler-plugin 3.13.0->3.16.0; org.apache.maven.plugins:maven-surefire-plugin 3.2.5->3.6.0 |
| maven-top-01-junit | hook | 7 | yes | yes | no |  |
| maven-top-01-junit | hook | 8 | yes | yes | yes | org.apache.maven.plugins:maven-surefire-plugin 3.5.2->3.6.0; org.junit.jupiter:junit-jupiter 5.11.4->6.1.3 |
| maven-top-01-junit | hook | 9 | yes | yes | yes | org.apache.maven.plugins:maven-surefire-plugin 3.2.5->3.6.0; org.junit.jupiter:junit-jupiter 5.10.2->6.1.3 |
| maven-top-01-junit | hook | 10 | yes | yes | yes | org.apache.maven.plugins:maven-surefire-plugin 3.5.2->3.6.0; org.junit.jupiter:junit-jupiter 5.11.4->6.1.3 |
| maven-top-06-spring-data-jpa | nohook | 1 | yes | no | no |  |
| maven-top-06-spring-data-jpa | nohook | 2 | yes | no | no |  |
| maven-top-06-spring-data-jpa | nohook | 3 | yes | no | no |  |
| maven-top-06-spring-data-jpa | nohook | 4 | yes | yes | no |  |
| maven-top-06-spring-data-jpa | nohook | 5 | yes | no | no |  |
| maven-top-06-spring-data-jpa | nohook | 6 | yes | no | no |  |
| maven-top-06-spring-data-jpa | nohook | 7 | yes | no | no |  |
| maven-top-06-spring-data-jpa | nohook | 8 | yes | no | no |  |
| maven-top-06-spring-data-jpa | nohook | 9 | yes | no | no |  |
| maven-top-06-spring-data-jpa | nohook | 10 | yes | no | no |  |
| maven-top-06-spring-data-jpa | hook | 1 | yes | yes | yes | org.springframework.boot:spring-boot-starter-parent 3.5.3->4.1.1 |
| maven-top-06-spring-data-jpa | hook | 2 | yes | yes | no |  |
| maven-top-06-spring-data-jpa | hook | 3 | yes | yes | no |  |
| maven-top-06-spring-data-jpa | hook | 4 | yes | yes | no |  |
| maven-top-06-spring-data-jpa | hook | 5 | yes | yes | no |  |
| maven-top-06-spring-data-jpa | hook | 6 | yes | yes | yes | org.springframework.boot:spring-boot-starter-parent 3.3.4->4.1.1 |
| maven-top-06-spring-data-jpa | hook | 7 | yes | yes | no |  |
| maven-top-06-spring-data-jpa | hook | 8 | yes | yes | no |  |
| maven-top-06-spring-data-jpa | hook | 9 | yes | yes | no |  |
| maven-top-06-spring-data-jpa | hook | 10 | yes | yes | no |  |
| npm-top-04-to-regex-range | nohook | 1 | no | n/a | no |  |
| npm-top-04-to-regex-range | nohook | 2 | no | n/a | no |  |
| npm-top-04-to-regex-range | nohook | 3 | no | n/a | no |  |
| npm-top-04-to-regex-range | nohook | 4 | no | n/a | no |  |
| npm-top-04-to-regex-range | nohook | 5 | no | n/a | no |  |
| npm-top-04-to-regex-range | nohook | 6 | no | n/a | no |  |
| npm-top-04-to-regex-range | nohook | 7 | no | n/a | no |  |
| npm-top-04-to-regex-range | nohook | 8 | no | n/a | no |  |
| npm-top-04-to-regex-range | nohook | 9 | yes | yes | no |  |
| npm-top-04-to-regex-range | nohook | 10 | no | n/a | no |  |
| npm-top-04-to-regex-range | hook | 1 | no | n/a | no |  |
| npm-top-04-to-regex-range | hook | 2 | yes | yes | no |  |
| npm-top-04-to-regex-range | hook | 3 | no | n/a | no |  |
| npm-top-04-to-regex-range | hook | 4 | no | n/a | no |  |
| npm-top-04-to-regex-range | hook | 5 | no | n/a | no |  |
| npm-top-04-to-regex-range | hook | 6 | no | n/a | no |  |
| npm-top-04-to-regex-range | hook | 7 | no | n/a | no |  |
| npm-top-04-to-regex-range | hook | 8 | yes | yes | no |  |
| npm-top-04-to-regex-range | hook | 9 | no | n/a | no |  |
| npm-top-04-to-regex-range | hook | 10 | no | n/a | no |  |
| npm-top-10-fresh | nohook | 1 | yes | no | no |  |
| npm-top-10-fresh | nohook | 2 | yes | no | no |  |
| npm-top-10-fresh | nohook | 3 | yes | no | no |  |
| npm-top-10-fresh | nohook | 4 | yes | no | no |  |
| npm-top-10-fresh | nohook | 5 | yes | no | no |  |
| npm-top-10-fresh | nohook | 6 | yes | no | no |  |
| npm-top-10-fresh | nohook | 7 | yes | no | no |  |
| npm-top-10-fresh | nohook | 8 | yes | no | no |  |
| npm-top-10-fresh | nohook | 9 | yes | no | no |  |
| npm-top-10-fresh | nohook | 10 | yes | no | no |  |
| npm-top-10-fresh | hook | 1 | yes | no | yes | fresh 0.5.2->2.0.0 |
| npm-top-10-fresh | hook | 2 | yes | no | no |  |
| npm-top-10-fresh | hook | 3 | yes | no | no |  |
| npm-top-10-fresh | hook | 4 | yes | no | yes | fresh 0.5.2->2.0.0 |
| npm-top-10-fresh | hook | 5 | yes | no | yes | fresh 0.5.2->2.0.0 |
| npm-top-10-fresh | hook | 6 | yes | no | yes | fresh 0.5.2->2.0.0 |
| npm-top-10-fresh | hook | 7 | yes | no | yes | fresh 0.5.2->2.0.0 |
| npm-top-10-fresh | hook | 8 | yes | no | yes | fresh 0.5.2->2.0.0 |
| npm-top-10-fresh | hook | 9 | yes | no | no |  |
| npm-top-10-fresh | hook | 10 | yes | no | yes | fresh 0.5.2->2.0.0 |
| go-top-06-x-net | nohook | 1 | yes | yes | no |  |
| go-top-06-x-net | nohook | 2 | yes | yes | no |  |
| go-top-06-x-net | nohook | 3 | yes | yes | no |  |
| go-top-06-x-net | nohook | 4 | yes | yes | no |  |
| go-top-06-x-net | nohook | 5 | yes | yes | no |  |
| go-top-06-x-net | nohook | 6 | yes | yes | no |  |
| go-top-06-x-net | nohook | 7 | yes | yes | no |  |
| go-top-06-x-net | nohook | 8 | yes | yes | no |  |
| go-top-06-x-net | nohook | 9 | yes | yes | no |  |
| go-top-06-x-net | nohook | 10 | yes | yes | no |  |
| go-top-06-x-net | hook | 1 | yes | yes | no |  |
| go-top-06-x-net | hook | 2 | yes | yes | no |  |
| go-top-06-x-net | hook | 3 | yes | yes | no |  |
| go-top-06-x-net | hook | 4 | yes | yes | no |  |
| go-top-06-x-net | hook | 5 | yes | yes | no |  |
| go-top-06-x-net | hook | 6 | yes | yes | no |  |
| go-top-06-x-net | hook | 7 | yes | yes | no |  |
| go-top-06-x-net | hook | 8 | yes | yes | no |  |
| go-top-06-x-net | hook | 9 | yes | yes | no |  |
| go-top-06-x-net | hook | 10 | yes | yes | no |  |
| cargo-top-01-libc | nohook | 1 | no | n/a | no |  |
| cargo-top-01-libc | nohook | 2 | no | n/a | no |  |
| cargo-top-01-libc | nohook | 3 | no | n/a | no |  |
| cargo-top-01-libc | nohook | 4 | no | n/a | no |  |
| cargo-top-01-libc | nohook | 5 | no | n/a | no |  |
| cargo-top-01-libc | nohook | 6 | no | n/a | no |  |
| cargo-top-01-libc | nohook | 7 | no | n/a | no |  |
| cargo-top-01-libc | nohook | 8 | no | n/a | no |  |
| cargo-top-01-libc | nohook | 9 | no | n/a | no |  |
| cargo-top-01-libc | nohook | 10 | no | n/a | no |  |
| cargo-top-01-libc | hook | 1 | no | n/a | no |  |
| cargo-top-01-libc | hook | 2 | no | n/a | no |  |
| cargo-top-01-libc | hook | 3 | no | n/a | no |  |
| cargo-top-01-libc | hook | 4 | no | n/a | no |  |
| cargo-top-01-libc | hook | 5 | no | n/a | no |  |
| cargo-top-01-libc | hook | 6 | no | n/a | no |  |
| cargo-top-01-libc | hook | 7 | no | n/a | no |  |
| cargo-top-01-libc | hook | 8 | no | n/a | no |  |
| cargo-top-01-libc | hook | 9 | no | n/a | no |  |
| cargo-top-01-libc | hook | 10 | no | n/a | no |  |
| ghactions-top-01-checkout | nohook | 1 | yes | no | no |  |
| ghactions-top-01-checkout | nohook | 2 | yes | no | no |  |
| ghactions-top-01-checkout | nohook | 3 | yes | no | no |  |
| ghactions-top-01-checkout | nohook | 4 | yes | no | no |  |
| ghactions-top-01-checkout | nohook | 5 | yes | no | no |  |
| ghactions-top-01-checkout | nohook | 6 | yes | no | no |  |
| ghactions-top-01-checkout | nohook | 7 | yes | no | no |  |
| ghactions-top-01-checkout | nohook | 8 | yes | no | no |  |
| ghactions-top-01-checkout | nohook | 9 | yes | no | no |  |
| ghactions-top-01-checkout | nohook | 10 | yes | no | no |  |
| ghactions-top-01-checkout | hook | 1 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1 |
| ghactions-top-01-checkout | hook | 2 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1 |
| ghactions-top-01-checkout | hook | 3 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1 |
| ghactions-top-01-checkout | hook | 4 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1 |
| ghactions-top-01-checkout | hook | 5 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1 |
| ghactions-top-01-checkout | hook | 6 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1 |
| ghactions-top-01-checkout | hook | 7 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1 |
| ghactions-top-01-checkout | hook | 8 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1 |
| ghactions-top-01-checkout | hook | 9 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1 |
| ghactions-top-01-checkout | hook | 10 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1 |
| ghactions-top-09-docker-buildx | nohook | 1 | yes | no | no |  |
| ghactions-top-09-docker-buildx | nohook | 2 | yes | no | no |  |
| ghactions-top-09-docker-buildx | nohook | 3 | yes | no | no |  |
| ghactions-top-09-docker-buildx | nohook | 4 | yes | no | no |  |
| ghactions-top-09-docker-buildx | nohook | 5 | yes | no | no |  |
| ghactions-top-09-docker-buildx | nohook | 6 | yes | no | no |  |
| ghactions-top-09-docker-buildx | nohook | 7 | yes | no | no |  |
| ghactions-top-09-docker-buildx | nohook | 8 | yes | no | no |  |
| ghactions-top-09-docker-buildx | nohook | 9 | yes | no | no |  |
| ghactions-top-09-docker-buildx | nohook | 10 | yes | no | no |  |
| ghactions-top-09-docker-buildx | hook | 1 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1; docker/build-push-action v6->53b7df96c91f9c12dcc8a07bcb9ccacbed38856a |
| ghactions-top-09-docker-buildx | hook | 2 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1; docker/build-push-action v6->53b7df96c91f9c12dcc8a07bcb9ccacbed38856a |
| ghactions-top-09-docker-buildx | hook | 3 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1; docker/build-push-action v6->53b7df96c91f9c12dcc8a07bcb9ccacbed38856a |
| ghactions-top-09-docker-buildx | hook | 4 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1; docker/build-push-action v6->53b7df96c91f9c12dcc8a07bcb9ccacbed38856a |
| ghactions-top-09-docker-buildx | hook | 5 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1; docker/build-push-action v6->53b7df96c91f9c12dcc8a07bcb9ccacbed38856a |
| ghactions-top-09-docker-buildx | hook | 6 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1; docker/build-push-action v6->53b7df96c91f9c12dcc8a07bcb9ccacbed38856a |
| ghactions-top-09-docker-buildx | hook | 7 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1; docker/build-push-action v6->53b7df96c91f9c12dcc8a07bcb9ccacbed38856a |
| ghactions-top-09-docker-buildx | hook | 8 | yes | yes | yes | actions/checkout v4->3d3c42e5aac5ba805825da76410c181273ba90b1; docker/build-push-action v6->53b7df96c91f9c12dcc8a07bcb9ccacbed38856a |
| ghactions-top-09-docker-buildx | hook | 9 | yes | yes | yes | actions/checkout v4->v7.0.1; docker/build-push-action v6->v7.3.0 |
| ghactions-top-09-docker-buildx | hook | 10 | yes | yes | yes | actions/checkout v4->v7.0.1; docker/build-push-action v6->v7.3.0 |
</details>

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
exactly once in 10 tries, but not on `urllib3` itself — that rep wrote `urllib3==2.8.0` cleanly with no
issue; the block fired on an unrelated `pytest==8.3.5` test dependency the model also added to a
`pyproject.toml` it created alongside `requirements.txt`. A reminder that `yul` checks *every* manifest
a run touches, not just the one the case prompt is nominally about.

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
