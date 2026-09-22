# opencode-yul

Forces LLMs to use the latest release of dependencies instead of them 
writing the outdated version from training data.

This outdated version could be a security vulnerability, a bug, or just a 
missing feature.
Thus, this plugin for OpenCode solves the problem by blocking the write/edit 
tool call if it adds a dependency older than the latest version.

Supported ecosystems: Maven Central, PyPI, npm, GitHub Actions, Go modules, crates.io.

## Install

Add it to the `plugin` array in an `opencode.json`/`opencode.jsonc`:

- **Project scope** (this project only): put it in `opencode.json`/`opencode.jsonc` at the project root.
- **User scope** (every project you open): put it in `~/.config/opencode/opencode.json`/`opencode.jsonc` instead.

```json
{
  "plugin": ["opencode-yul"]
}
```

## Update

OpenCode is supposed to re-resolve `@latest` and reinstall on its own, see [anomalyco/opencode#16998](https://github.com/anomalyco/opencode/pull/16998).
However, if you suspect you're stuck on an old version, force it yourself:

```sh
rm -rf ~/.cache/opencode/packages/opencode-yul@latest
```

Then start a new OpenCode session.
It reinstalls from scratch on next use.


