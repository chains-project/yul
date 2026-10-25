# Privacy

yul runs on your machine. It has no telemetry and sends nothing to the chains-project maintainers.

To check a dependency, yul asks its public registry for the latest version. The request carries the package name. It does not carry file contents, file paths, or source code. The registries are Maven Central, PyPI, npm, the Go module proxy, crates.io, and the GitHub API for Actions. Some lookups go to packages.ecosyste.ms instead. yul does not skip private packages, so an internal package name in a manifest is looked up like any other. Each of these services handles requests under its own privacy policy.

For GitHub Actions, yul uses a GitHub token if one is available in `GITHUB_TOKEN`, `GH_TOKEN`, or `gh auth token`. It sends the token only to api.github.com, to raise the rate limit.

The Claude Code plugin also contacts GitHub at session start. It downloads the pinned yul release and checks whether a newer one exists.

yul stores its binary and its scan results under `~/.cache/yul/` (or `$XDG_CACHE_HOME/yul/`). Scan results list outdated dependencies per project. Deleting the directory removes them.

Questions go to https://github.com/chains-project/yul/issues.
