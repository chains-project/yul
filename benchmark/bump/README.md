# bump

Pilot harness testing `yul` against real, historically build-breaking
dependency updates from [chains-project/bump](https://github.com/chains-project/bump)
(SANER 2024) instead of `yul`'s own synthetic `benchmark/cases.json`
scenarios.

Each BUMP case ships as a pair of Docker images (`-pre`, `-breaking`)
bracketing one real dependency-version bump that's known to break that
project's build/tests. This pilot only uses the `-pre` image (the
project's last known-good state) and asks Claude to upgrade the flagged
dependency, without telling it which version to pick — the question is
whether `yul`'s PreToolUse hook changes what Claude writes, and whether it
correctly distinguishes an outdated/hallucinated version from a legitimate
one.

## Layout

- `cases/<id>.json` — trimmed copy of the case's `data/benchmark/*.json`
  entry from chains-project/bump (checked in, tiny).
- `workdirs/` — **gitignored**. The actual extracted project checkout(s)
  per case, one subdirectory per condition (`pre/hook/`, `pre/nohook/`).
  Never commit these — they're full real-world project trees (hundreds of
  MB), not the small manifests/transcripts `benchmark/runs/` stores.
- `results/<id>.md` — the report for that case (checked in).

## Reproducing a case

1. Requires Docker running locally. Pull the `-pre` image named in the
   case's `preCommitReproductionCommand`, then find the project root with
   `docker inspect <image> --format '{{json .Config}}'` — the `WorkingDir`
   field (BUMP images consistently set it to the project's checkout path,
   e.g. `/quickfixj`).
2. Extract it: `docker create` the image, `docker cp
   <cid>:<workdir> workdirs/<case-id>-pre-src`, `docker rm` the container.
3. Build the local `yul` binary (`go build -o yul .` at the repo root, per
   the main `CLAUDE.md`'s "using yul on this repo itself" section).
4. Copy `<case-id>-pre-src/` fresh into `workdirs/<case-id>/pre/hook/` and
   `.../nohook/`, `git init` each (so `git rev-parse --show-toplevel` can't
   escape into the real `yul` checkout — same reason `benchmark/run_case.sh`
   does this), and write `.claude/settings.json` in each:
   - `hook/`: wire both `SessionStart` (`<yul-bin> scan`) and `PreToolUse`
     on `Write|Edit` (`<yul-bin>`) — mirrors the real plugin's
     `hooks/hooks.json`, not just `run_case.sh`'s PreToolUse-only pattern.
   - `nohook/`: `{}`.
5. Run `claude -p "<prompt>"` in each, same invocation shape as
   `benchmark/run_case.sh` (`--permission-mode bypassPermissions
   --setting-sources project --output-format stream-json --verbose
   --no-session-persistence`).
6. Compare the dependency version before/after in each condition, and grep
   `transcript.jsonl` for the yul hook's stderr block to see whether/what
   it flagged. Write the result to `results/<case-id>.md`.

Prompt wording matters: avoid "check for outdated/latest" phrasing, since
that tells Claude to go verify the registry itself, which defeats the
point of observing what version it reaches for on its own. Name the
action and the dependency (we already know which one BUMP flagged for a
given case) and nothing else, e.g. "Upgrade the `<group>:<artifact>`
dependency in this project."

Only one case has been run by hand so far (see `results/`). Turning this
into a scripted, `run_all.sh`-style batch runner across more BUMP cases is
deferred until this manual pass proves the pipeline is worth automating.
