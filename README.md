# yul

A Claude Code `PreToolUse` hook that keeps dependencies current. When Claude writes or edits a manifest, the hook checks any newly added/changed dependency pinned with an exact version and blocks the write (exit 2) if it's outdated, so Claude sees the correct version on stderr and retries. Other files and untouched dependencies pass through untouched; resolver/network errors fail open.

Supported manifests:
- `pom.xml` — Maven Central
- `requirements.txt` — PyPI, `==` pins only
- `pyproject.toml` — PyPI, `[project.dependencies]` / `[project.optional-dependencies]`, `==` pins only
- `package.json` — npm registry, `dependencies` / `devDependencies` / `optionalDependencies` / `peerDependencies`, exact version pins only
- `.github/workflows/*.yml`/`*.yaml` — GitHub Actions, `uses:` steps pinned to a version-like tag (branch names and commit SHAs are left alone)

## Install as a Claude Code plugin (recommended)

Inside Claude Code, run:

```
/plugin marketplace add chains-project/chains-hooks
/plugin install yul@chains-project
```

The install dialog lets you pick a scope (all your projects, or just the current one). That's it — the plugin registers the `PreToolUse` hook and, on session start, downloads the checksum-verified `yul` release binary matching the plugin version into `~/.cache/yul/`. Until the binary is present (first session, offline), the hook fails open. Plugin updates and binary updates are one event: the pinned version lives in the plugin manifest.

To enable it for everyone working in a repo, check this into the repo's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "chains-project": {
      "source": { "source": "github", "repo": "chains-project/chains-hooks" }
    }
  },
  "enabledPlugins": { "yul@chains-project": true }
}
```

## Manual install

If you have Go installed, this is the preferred way to install the `yul` binary yourself:

```sh
go install github.com/chains-project/yul@latest
```

This places the binary at `$(go env GOPATH)/bin`. Unlike a `curl | sh` script, `go install` builds from the module proxy over a verified, checksummed (`GONOSUMCHECK`/`go.sum`-backed) supply chain, so you're not piping an arbitrary internet script into your shell.

If you don't have Go installed:

```sh
curl -fsSL https://raw.githubusercontent.com/chains-project/yul/main/install.sh | sh
```

This downloads the right `yul` binary for your OS/arch from the [latest release](https://github.com/chains-project/yul/releases), verifies its checksum, and installs it to `~/.local/bin` (override with `YUL_INSTALL_DIR`; pin a version with `YUL_VERSION`).

## Manual usage

If you installed the binary manually instead of using the plugin, add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "/home/<user>/go/bin/yul",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

Point `command` at the installed binary's absolute path (`~/.local/bin/yul` if you used the installer above, or `$(go env GOPATH)/bin/yul` if you used `go install`) — never at `go run`: `go run` always exits 1 on program failure regardless of the program's actual exit code ([golang/go#17813](https://github.com/golang/go/issues/17813)), so a blocking exit 2 from this hook is flattened to exit 1, where `stderr` reports `exit status 2` but `exitCode` is `1`.
Claude Code treats exit 1 as a non-blocking error, so the write goes through instead of being blocked.

With `go run`, you can see below the exitCode is 1, but stderr reports exit status 2, so Claude Code treats it as a non-blocking error and lets the write go through instead of blocking it.
```json
{
  "parentUuid":"3d0b0198-4c4f-473d-aca8-81aae1c47ba4",
  "isSidechain":false,
  "attachment":{
    "type":"hook_non_blocking_error",
    "hookName":"PreToolUse:Write",
    "toolUseID":"toolu_01NSX9EDCBG15megDu54GHRp",
    "hookEvent":"PreToolUse",
    "stderr":"Failed with non-blocking status code: outdated dependencies, use these versions instead:\n  org.json:json  20240303 -> 20260522\nexit status 2",
    "stdout":"",
    "exitCode":1,
    "command":"/home/aman/go/bin/yul",
    "durationMs":5349
  },
  "type":"attachment",
  "uuid":"9d9d7c75-51f3-45be-9fcd-63fd70c2d9b4",
  "timestamp":"2026-07-10T01:30:29.184Z",
  "session_id":"e4f05218-9565-43ba-826e-a9a699736c52",
  "userType":"external",
  "entrypoint":"cli",
  "cwd":"/tmp/tmp",
  "sessionId":"8e78af27-6afe-4d9c-a562-baaf77b94169",
  "version":"2.1.206",
  "gitBranch":"HEAD"
}
```


### Example

Claude tries to write a `pom.xml` pinning `org.json:json` to `20240303`. The hook blocks it:

```
outdated dependencies, use these versions instead:
  org.apache.pdfbox:pdfbox  3.0.3 -> 3.0.8
```

```json
{
  "parentUuid": "53362172-27ca-446a-9709-589501ce4343",
  "isSidechain": false,
  "promptId": "3a98011e-3feb-4ee4-84a8-3d42b48815a0",
  "type": "user",
  "message": {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "content": "PreToolUse:Write hook error: [/home/aman/Desktop/chains/ai-bump/yul]: outdated dependencies, use these versions instead:\n  org.apache.pdfbox:pdfbox  3.0.3 -> 3.0.8\n",
        "is_error": true,
        "tool_use_id": "toolu_015xUvsjc8FWGVG3QoS2Tko9"
      }
    ]
  },
  "uuid": "92b6b32d-8116-41c7-8773-c5dcb36e110b",
  "timestamp": "2026-07-27T15:00:23.991Z",
  "toolUseResult": "Error: PreToolUse:Write hook error: [/home/aman/Desktop/chains/ai-bump/yul]: outdated dependencies, use these versions instead:\n  org.apache.pdfbox:pdfbox  3.0.3 -> 3.0.8\n",
  "toolDenialKind": "permission-rule",
  "sourceToolAssistantUUID": "53362172-27ca-446a-9709-589501ce4343",
  "session_id": "00454dc4-731b-4ec8-8263-a1741b2c6a1e",
  "userType": "external",
  "entrypoint": "cli",
  "cwd": "/tmp/test",
  "sessionId": "00454dc4-731b-4ec8-8263-a1741b2c6a1e",
  "version": "2.1.220",
  "gitBranch": "HEAD"
}
```

Claude reads this from stderr and rewrites the manifest with the correct version.
