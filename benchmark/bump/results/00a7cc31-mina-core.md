# quickfixj / mina-core — yul vs. a real BUMP breaking-update

Case: chains-project/bump commit `00a7cc31784ac4a9cc27d506a73ae589d6df36d6`
(quickfixj, [PR #502](https://github.com/quickfix-j/quickfixj/pull/502)).
BUMP recorded `org.apache.mina:mina-core` 2.1.5 → 2.2.1 as a real,
historically build-breaking update (`COMPILATION_FAILURE`).

Project extracted from the `-pre` Docker image
(`ghcr.io/chains-project/breaking-updates:00a7cc31...-pre`, `WorkingDir
/quickfixj`), where `quickfixj-core/pom.xml` pins `mina-core` at `2.1.5`.

Prompt (identical in both runs, deliberately avoids "latest"/"outdated"
wording so Claude isn't told to go verify the registry):

> "Upgrade the org.apache.mina:mina-core dependency in this project."

| run | dependency before | dependency Claude wrote | did yul detect anything? |
|---|---|---|---|
| `nohook` | 2.1.5 | **2.2.9** | n/a (hook disabled) |
| `hook` (before fix) | 2.1.5 | **2.2.9** | **Yes — a false positive.** yul blocked the first `Edit` attempt with `"org.apache.mina:mina-core version 2.2.9 was never published - hallucinated version"`. The version is real. Claude retried the identical edit 26s later and it passed cleanly. |
| `hook` (fix v1: HTTP direct) | 2.1.5 | **2.2.9** | No false block — a single `Edit` call, accepted on the first try. |
| `hook` (fix v2: `git-pkgs/registries` v0.9.1, final) | 2.1.5 | **2.2.4** | No false block — a single `Edit` call, accepted on the first try. But see "open question" below: `2.2.4` is not actually the current latest (`2.2.9` is), and yul didn't flag it as outdated either. |

## Neither run reproduced BUMP's breaking version

In both conditions Claude landed on `2.2.9` (today's actual latest stable
release, correctly skipping the `3.0.0-M2` pre-release milestone) — not
BUMP's `2.2.1`. It got there by running `curl` against Maven Central's
`maven-metadata.xml` itself, on its own initiative, in *both* runs — not
just the hook run. So the minimal, non-"latest"-worded prompt didn't stop
Claude from independently verifying the registry; it just does that anyway
when asked to "upgrade" something. That's a useful negative result: this
prompt style doesn't reliably surface memorized/stale-version behavior for
a capable agent with shell access, at least not for this dependency.

## The actual finding: a false-positive hallucination flag

Timeline from the `hook` run's transcript (`transcript.jsonl`):

- `21:38:31.180Z` — Claude's first `Edit` (`2.1.5` → `2.2.9`) is rejected by
  yul: `PreToolUse:Edit hook error: [...]/yul: problems with new
  dependencies: org.apache.mina:mina-core version 2.2.9 was never published
  - hallucinated version`
- `21:38:43–47Z` — Claude re-checks independently: `curl
  .../mina-core/maven-metadata.xml` (lists `2.2.9` in `<versions>`), then
  `curl -o /dev/null -w '%{http_code}' .../mina-core/2.2.9/` → `200`.
- `21:38:57.851Z` — Claude retries the *identical* edit. It passes.

Independently reproduced after the fact: `maven-metadata.xml` lists `2.2.9`,
and `GET https://repo1.maven.org/maven2/org/apache/mina/mina-core/2.2.9/`
returns `200`. So this version has been published all along — yul's first
check was wrong.

## Root cause and fix

Initially assumed this was `repo1.maven.org` CDN edge inconsistency. It
wasn't — closer inspection during this pilot found the working tree
actually had an **uncommitted regression**: `main.go` and
`pkg/maven/existence.go` had been switched (without a commit) from the
documented `MavenCentralExistenceChecker` (direct HTTP against
`repo1.maven.org`'s static CDN) to a `RegistryExistenceChecker` going
through `git-pkgs/enrichment`'s client, which hits Maven Central's Solr
endpoint (`search.maven.org`) — exactly what `CLAUDE.md` already documents
as unreliable ("returns found/not-found/timeout inconsistently... hands
back version lists with every version string stripped"). That's what
actually produced the flaky false positive.

Fix applied in this session:
- Reimplemented `pkg/maven/existence.go`'s `MavenCentralExistenceChecker`
  per `CLAUDE.md`'s documented design: GET the version directory
  (`<group>/<artifact>/<version>/`) first — 200 confirms the release
  directly; a 404 is now **retried once, after a 300ms backoff**, before
  falling back to a `maven-metadata.xml` GET to tell "wrong version"
  (`KindMissingVersion`) apart from "wrong package entirely"
  (`KindMissingPackage`). Any other status or a transport error still
  fails open, unretried.
- Reverted `main.go` back to `maven.NewMavenCentralExistenceChecker()`.
- Rewrote `pkg/maven/existence_test.go` for the new implementation,
  including a test (`TestMavenCentralExistenceRetryRecoversFromTransient
  NotFound`) that reproduces a transient 404 and asserts the retry
  recovers.
- `go mod tidy` (drops `git-pkgs/registries` back to an indirect
  dependency). `go build ./...`, `go vet ./...`, `go test ./...` all pass.

Re-ran the `hook` condition with the fixed binary: a single `Edit` call,
accepted immediately — no false block, no retry needed this time (see
table above).

## Direction change: use `git-pkgs/registries`, not raw HTTP

Mid-session, the user pointed out they'd already fixed the *actual* root
cause of `git-pkgs/registries`' version-list bug upstream: PR
[git-pkgs/registries#82](https://github.com/git-pkgs/registries/pull/82)
("maven: decode the version from the Solr `v` field, not `latestVersion`"),
authored together with a prior Claude Code session, merged into `main` and
released as `v0.9.1`. That fix addresses a *different* problem than the one
this pilot first hit: PR #82 fixes `GetVersions` returning every version as
an empty string (a decoding bug); the false positive here was Solr's
own found/not-found *search-index lag* for a specific query, which no
parsing fix touches.

Decision: keep using `git-pkgs/registries` (now `v0.9.1`, pinned directly
in `go.mod`) via `RegistryExistenceChecker`, rather than the raw-HTTP
`MavenCentralExistenceChecker` built earlier in this session (removed).
Added the same one-retry/300ms-backoff safeguard to `RegistryExistenceChecker`
instead, covering both a `registries.ErrNotFound` and a "version not in an
otherwise-real list" result. `main.go` wired back to
`maven.NewRegistryExistenceChecker()`; `CLAUDE.md` and
`benchmark/hallucination/compare.go`'s header updated to describe this as
the current, intended design (not something to avoid).

Re-ran the `hook` condition once more against this final binary — see the
third table row above.

## Open question raised by the final run (not resolved)

The final run's `Edit` (`2.1.5` → `2.2.4`) passed with no block at all —
correct on existence (`2.2.4` is a real, published version), but `2.2.4`
is **not** yul's separately-reported latest: querying
`resolver.EnrichmentResolver.LatestVersions` directly, moments after this
run, for `pkg:maven/org.apache.mina/mina-core` returned `2.2.9`. So either
yul's *outdated* check (a different code path,
`pkg/util/resolver/enrichment.go`, using `enrichment.NewClient()` rather
than `RegistryExistenceChecker`'s direct registries client, unaffected by
this session's retry fix) saw a stale answer at the moment of that
specific hook invocation, or something else about that pin's evaluation
skipped it. Not chased down further in this pilot — flagged here since it
suggests the *outdated*-version resolver may have its own transient
staleness exposure, structurally similar to what was just fixed for
*existence*, but with no retry safeguard of its own.

## Secondary finding (not fixed, informational)

`yul scan`'s `SessionStart` report on this project flagged 34 problems,
most of them real outdated pins — but several were
`org.quickfixj:quickfixj-parent`/`quickfixj-examples` pinned at
`3.0.0-SNAPSHOT` across the multi-module build, reported as "hallucinated
version." That's a Maven reactor pattern (a multi-module project's
sub-modules referencing their own in-progress `SNAPSHOT` parent, resolved
locally during a reactor build, never published to Central) — not a model
hallucination. `MavenCentralExistenceChecker` has no way to know a pin
refers to a sibling module in the same reactor rather than an external
coordinate, so every intra-project `SNAPSHOT` reference in a multi-module
`pom.xml` will currently misreport as `KindMissingVersion`. Left alone for
this pilot; flagging here since it's a distinct false-positive class from
the retry fix above.

## Artifacts

Full transcripts and final `pom.xml`s are under
`benchmark/bump/workdirs/00a7cc31-mina-core/pre/{hook,nohook}/`
(gitignored — not checked in, real 270MB+ project checkout).
