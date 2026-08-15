# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`yul` is a Claude Code `PreToolUse` hook (Go binary) that keeps dependencies current. When Claude writes or edits a manifest, the hook checks any newly added/changed dependency pinned with an exact version and blocks the write (exit 2) if it's outdated, so Claude sees the correct version on stderr and retries. Other files and untouched dependencies pass through untouched; resolver/network errors fail open (exit 0).

Supported manifests: `pom.xml` (Maven Central), `requirements.txt` and `pyproject.toml` (PyPI, `==` pins only), `package.json` (npm, exact pins across all four dependency fields), `.github/workflows/*.yml`/`*.yaml` (GitHub Actions, `uses:` steps pinned to a version-like tag — branch names and commit SHAs are left alone).

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

The repo doubles as a Claude Code plugin and its own marketplace (`/plugin marketplace add chains-project/yul`, then `/plugin install yul@chains-project`):

- `.claude-plugin/plugin.json` — manifest; its `version` pins which release binary the plugin downloads, and bumping it is the marketplace's update signal (only the release workflow writes it).
- `.claude-plugin/marketplace.json` — makes the repo directly installable (plugin source `./`).
- `hooks/hooks.json` — `SessionStart` runs `scripts/ensure-yul.sh` (downloads the pinned release binary into `~/.cache/yul/v<version>/` via `install.sh`, always exits 0); `PreToolUse` on `Write|Edit` runs `scripts/hook.sh` (execs the cached binary, exits 0 if it's missing — fail open).

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

`.claude/settings.json` wires `yul` up as this repo's own `PreToolUse` hook for `Write`, pointed at the locally built binary at the repo root via `$CLAUDE_PROJECT_DIR/yul` (Claude Code sets `$CLAUDE_PROJECT_DIR` to the project root when running hooks, so the shared config works on any checkout) — so writing a manifest in this repo while developing exercises the hook against itself. Build the binary once with `go build -o yul .`; until it exists the hook is a silent no-op. Rebuild it after changing checker/resolver code for the hook to pick up the change. Personal hook/settings overrides go in `.claude/settings.local.json` (gitignored).
