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

Releases go through `.goreleaser.yml` (triggered by `.github/workflows/release.yml`), building linux/darwin amd64/arm64 binaries with `-X main.version={{.Tag}}`. `install.sh` downloads the right release binary, verifies its checksum, and installs to `~/.local/bin`.

There is no linter config in this repo beyond `go vet`/`gofmt` defaults.

## Benchmark

> [!WARNING]
> This burns A LOT of tokens!

`benchmark/` evaluates the hook empirically rather than via `go test`: `run_all.sh <cases.json> <output_dir> [parallelism]` runs each case in `cases.json` under both `hook` and `nohook` conditions in parallel, invoking `run_case.sh`, which drives `claude -p` non-interactively (`--permission-mode bypassPermissions`) and captures the full turn-by-turn transcript (`transcript.jsonl`) plus the resulting manifest (`final_manifest`) per run. `benchmark/runs/` holds recorded runs per case (e.g. `ghactions-01-checkout-test`, `maven-03-okhttp`, `npm-04-react`, `pyproject-02-pydantic`).

## PR conventions

- Title starts with a Conventional Commits keyword (`feat:`, `fix:`, `refactor:`, `test:`, `chore:`, `docs:`, etc).
- Description is just a summary of the change and the old vs. new behavior, using text/code block snippets (e.g. before/after output) where useful to show the difference. No test plan section.

## Using yul on this repo itself

`.claude/settings.json` wires `yul` up as this repo's own `PreToolUse` hook for `Write`, pointed at the locally built binary at the repo root (`./yul`) — so writing a manifest in this repo while developing exercises the hook against itself. Rebuild that binary (`go build -o yul .`) after changing checker/resolver code for the hook to pick up the change.
