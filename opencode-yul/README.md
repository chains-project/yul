# opencode-yul

[OpenCode](https://opencode.ai) plugin version of [`yul`](https://github.com/chains-project/yul): keeps dependencies current by blocking `write`/`edit` tool calls that would pin a dependency to a version older than what's actually released, so the agent sees the current version and retries instead of leaving a stale pin from its training data.

## Install

Add it to your project's `opencode.json`/`opencode.jsonc`:

```json
{
  "plugin": ["opencode-yul"]
}
```

That's it. On first use, the plugin downloads the pinned `yul` release binary (checksum-verified) into `~/.cache/yul/v<version>/` and reuses it on every session after. If the download fails, is still in progress, or hits a permissions error, the plugin fails open — writes/edits go through as normal.

## What it catches

When a `write`/`edit` tool call pins a newly added/changed dependency in a supported manifest (`pom.xml`, `requirements.txt`, `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `.github/workflows/*.yml`) to an exact version older than the latest release, the call is blocked with the current version in the error message, so the agent can retry with it. Untouched dependencies and other files pass through unchanged; resolver/network errors fail open.

See the [main `yul` README](https://github.com/chains-project/yul#readme) for the full list of supported manifests, how version resolution works per ecosystem, and the Claude Code plugin this mirrors.
