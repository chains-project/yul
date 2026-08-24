# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`yul` is a Claude Code `PreToolUse` hook (Go binary) that keeps dependencies current. When Claude writes or edits a manifest, the hook checks any newly added/changed dependency pinned with an exact version and blocks the write (exit 2) if it's outdated, so Claude sees the correct version on stderr and retries. Other files and untouched dependencies pass through untouched; resolver/network errors fail open (exit 0).

Supported manifests: `pom.xml` (Maven Central), `requirements.txt` and `pyproject.toml` (PyPI, `==` pins only), `package.json` (npm, exact pins across all four dependency fields), `.github/workflows/*.yml`/`*.yaml` (GitHub Actions, `uses:` steps pinned to a version-like tag — branch names and commit SHAs are left alone), `go.mod` (Go modules, `require` entries — every entry is inherently an exact pin, since go.mod has no range syntax), `Cargo.toml` (crates.io, `=` pins only — a bare version like `"1.2.3"` is Cargo's implicit caret range, not an exact pin), `Podfile` (CocoaPods, exact pins only — a `~>` pessimistic-operator constraint is a range, not a pin), `MODULE.bazel` (Bazel modules/bzlmod, `bazel_dep` entries — every entry is inherently an exact pin, since bzlmod has no range syntax).

## Commands

```sh
go build ./...
go test ./... -v
go test ./pkg/npm/...          # single package
go test ./pkg/npm/ -run TestX  # single test
```

CI (`.github/workflows/test.yml`) just runs `go build ./...` and `go test ./... -v` on push/PR to `main`.

Releases are cut by manually dispatching `.github/workflows/release.yml` (Actions → Release → Run workflow) with a `patch` or `minor` bump — never by pushing a tag. The workflow bumps `version` in `.claude-plugin/plugin.json`, commits `Release vX.Y.Z` to `main`, tags that commit, pushes both, then runs goreleaser (`.goreleaser.yml`, linux/darwin amd64/arm64 binaries with `-X main.version={{.Tag}}`). Major bumps are deliberately not offered (a v2 module path would break `go install github.com/chains-project/yul@latest`); the workflow refuses to produce a major version >1. `install.sh` downloads the right release binary, verifies its checksum, and installs to `~/.local/bin` by default.

## Claude Code plugin

The repo is packaged as a Claude Code plugin, distributed through the org marketplace hosted in [chains-project/chains-hooks](https://github.com/chains-project/chains-hooks) (`/plugin marketplace add chains-project/chains-hooks`, then `/plugin install yul@chains-project`):

- `.claude-plugin/plugin.json` — manifest; its `version` pins which release binary the plugin downloads, and bumping it is the marketplace's update signal (only the release workflow writes it).
- `hooks/hooks.json` — `SessionStart` runs `scripts/ensure-yul.sh` (downloads the pinned release binary into `~/.cache/yul/v<version>/` via `install.sh`, always exits 0), then `scripts/session-scan.sh` (execs the cached binary's `scan` subcommand); `PreToolUse` on `Write|Edit` runs `scripts/hook.sh` (execs the cached binary, exits 0 if it's missing — fail open).
- The `chains-hooks` marketplace source for `yul` is unpinned, but Claude Code doesn't re-resolve a plugin's source on every session — it reuses whatever it last cloned into `~/.claude/plugins/cache/<marketplace>/yul/`. Claude Code *can* auto-update a plugin in the background a few minutes after session start, but that's off by default for third-party marketplaces (only Anthropic's official ones default to on), so a user can end up running a stale plugin version indefinitely with no signal that a newer one exists. `ensure-yul.sh` also checks GitHub's latest release tag against the plugin version it resolved this session and, if newer, prints a top-level `systemMessage` — shown straight to the user's terminal, the same channel Claude Code uses for its own update notices, as opposed to `hookSpecificOutput.additionalContext` (used elsewhere for the scan findings) which only Claude sees. The message points users at `claude plugin update yul@chains-project` for an immediate pickup, and at adding `"autoUpdate": true` to the `chains-project` entry under `extraKnownMarketplaces` — in whichever of `~/.claude/settings.json` (user scope), `.claude/settings.json` (project scope), or `.claude/settings.local.json` (local scope) it's registered in — to fix it durably. This check fails open like the rest of the script.

## Project-wide scan

The `PreToolUse` hook only checks dependencies a Write/Edit just touched. `yul scan` (in `main.go`, backed by `pkg/scan`) instead walks the whole project once per session, via the second `SessionStart` hook above, and reports every exactly-pinned dependency across all known manifest kinds that's older than the latest release — by reusing each ecosystem's `Check(before, after)` with `before=""`, so every pin counts as "new". Findings are cached per project directory (`pkg/scan.Cache`, keyed by a hash of the absolute path under `~/.cache/yul/scan/`) for `scanCacheTTL` (one week); a cache is only reused if it was written by the same yul `version` (an upgrade always forces a rescan) *and* `scan.Hash` of the current manifest contents still matches `ManifestsHash` from when the cache was written — `Hash` is network-free (only `Filename`/`MatchesPath` matching, no resolver calls) so it's cheap to check on every session start, and it's what makes a manifest edited by hand (or by anything other than the PreToolUse hook) get picked up immediately instead of waiting out the TTL. If there are findings, `runScan` prints `SessionStart` hook JSON with `hookSpecificOutput.additionalContext` telling Claude to ask the user before updating anything; if the project is clean or nothing changed since the last scan, it prints nothing.

Test the plugin locally with `claude --plugin-dir .` and `claude plugin validate .`.

There is no linter config in this repo beyond `go vet`/`gofmt` defaults.

## Benchmark

> [!WARNING]
> This burns A LOT of tokens!

`benchmark/` evaluates the hook empirically rather than via `go test`: `run_all.sh <cases.json> <output_dir> [parallelism]` runs each case in `cases.json` under both `hook` and `nohook` conditions in parallel, invoking `run_case.sh`, which drives `claude -p` non-interactively (`--permission-mode bypassPermissions`) and captures the full turn-by-turn transcript (`transcript.jsonl`) plus the resulting manifest (`final_manifest`) per run. `benchmark/runs/` holds recorded runs per case (e.g. `ghactions-01-checkout-test`, `maven-03-okhttp`, `npm-04-react`, `pyproject-02-pydantic`).

## PR conventions

- Title starts with a Conventional Commits keyword (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`, `docs:`, etc).
- Description is just a summary of the change and the old vs. new behavior, using text/code block snippets (e.g. before/after output) where useful to show the difference. No test plan section.

## Using yul on this repo itself

`.claude/settings.json` enables the `yul` plugin at project scope (`extraKnownMarketplaces` + `enabledPlugins`), so anyone opening this repo in Claude Code gets the hook after accepting the trust prompt — running the pinned **release** binary from `~/.cache/yul/`, not your working tree. To exercise a locally built binary while developing, build it with `go build -o yul .` and wire it up in `.claude/settings.local.json` (gitignored):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "\"$CLAUDE_PROJECT_DIR\"/yul", "timeout": 30 }
        ]
      }
    ]
  }
}
```

Rebuild the binary after changing checker/resolver code for the hook to pick up the change. Note both hooks run in this setup — the local one and the plugin's release binary.
