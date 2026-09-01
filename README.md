# yul

A Claude Code `PreToolUse` hook that keeps dependencies current. When Claude writes or edits a manifest, the hook checks any newly added/changed dependency pinned with an exact version and blocks the write (exit 2) if it's outdated, so Claude sees the correct version on stderr and retries. Other files and untouched dependencies pass through untouched; resolver/network errors fail open.

Supported manifests:
- `pom.xml` — Maven Central
- `requirements.txt` — PyPI, `==` pins only
- `pyproject.toml` — PyPI, `[project.dependencies]` / `[project.optional-dependencies]`, `==` pins only
- `package.json` — npm registry, `dependencies` / `devDependencies` / `optionalDependencies` / `peerDependencies`, exact version pins only
- `.github/workflows/*.yml`/`*.yaml` — GitHub Actions, `uses:` steps pinned to a version-like tag (branch names and commit SHAs are left alone)
- `go.mod` — Go modules, `require` entries (single-line and block form, direct and indirect)
- `Cargo.toml` — crates.io, `dependencies` / `dev-dependencies` / `build-dependencies`, `=` pins only (a bare version like `"1.2.3"` is Cargo's implicit caret range, not an exact pin)
- `MODULE.bazel` — Bazel modules (bzlmod), `bazel_dep` entries (dev and non-dev)

## Install as a Claude Code plugin (recommended)

Inside Claude Code, run:

```
/plugin marketplace add chains-project/chains-hooks
/plugin install yul@chains-project
```

The install dialog lets you pick a scope (all your projects, or just the current one). That's it — nothing is written to your `settings.json` beyond enabling the plugin; the hook wiring ships inside the plugin itself (`hooks/hooks.json`), which Claude Code discovers when it clones this repo and registers on every session:

- **On session start**, `scripts/ensure-yul.sh` downloads the checksum-verified release binary pinned by `.claude-plugin/plugin.json` into `~/.cache/yul/v<version>/`. Once the binary is there, this is an instant no-op; on any failure it exits 0 and never blocks the session.

Plugin updates and binary updates are automated. Whenever we update `yul`, claude will get the updated release.

### Enabling it for a whole team

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

The `extraKnownMarketplaces` entry matters: it tells collaborators' Claude Code where `yul@chains-project` lives, so they don't need to have added the marketplace themselves.

Collaborators then don't run any install commands. The first time they start Claude Code in the repo, it reads the checked-in settings, asks them to confirm they trust the `chains-project` marketplace and the `yul` plugin, and — once accepted — installs the plugin and downloads the release binary on session start. Declining just leaves the plugin disabled for them; nothing else breaks. Updates are picked up automatically as new plugin versions are released.

## Manual install

> [!NOTE] Prefer this method if you want control over which version you run.
> The `/plugin` installs above updates automatically as new releases ship.

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

#### Hook blocks a stale pin

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

#### Initial scan

If you are already working on a project and then you install the hook,
`yul` does an init-scan and asks you if you want to update any stale pins it finds. If you say yes,
it updates on the fly, else, it remembers your decision and does not prompt 
you later.

![init-scan](docs/init-scan.png)


## Why some ecosystems need this more than others

`yul` only ever fires on a manifest write that hand-pins an exact, already-stale version. Some ecosystems have a CLI command that resolves and writes the latest version for you, so Claude reaches for that instead of typing a version number — which means there's nothing stale for the hook to catch. Others have no such command, so Claude has to type a version from memory (often stale, since that's frozen at training time), which is exactly the case `yul` is built to guard.

This was observed empirically across the `benchmark/` scaffolding runs (see [`benchmark/runs`](benchmark/runs), and the [write-up](https://chains.proj.kth.se/ai-bump.html)): in the `nohook` condition, Claude's own tool choice split cleanly along these lines.

| Ecosystem | Direct "give me latest" command? | What Claude actually did (nohook) |
| --- | --- | --- |
| Go (`go.mod`) | Yes — `go get <module>` / `go mod tidy` | Ran `go get`, which hits the module proxy and writes the resolved latest version itself. Nothing to catch. |
| npm (`package.json`) | Yes — `npm install <pkg>` | Ran `npm install`, which resolves the latest release and writes it (as a `^` range) at install time, before any Write/Edit reaches the hook. |
| pip (`requirements.txt`) | No | `pip install <pkg>` installs into the venv but doesn't add the package to `requirements.txt` — Claude typed the line by hand (often unpinned, or an exact `==` pin recalled from memory). |
| PyPI (`pyproject.toml`) | No | Same gap as pip — no command resolves a version straight into `[project.dependencies]`, so Claude hand-typed the pin (or a `>=` range). |
| Maven (`pom.xml`) | No | There's no Maven equivalent of `npm install`/`go get` that adds a resolved `<dependency>` block; Claude always hand-typed the `<version>`. |
| GitHub Actions (`uses:` tags) | No | Action versions are git tags on someone else's repo — there's no registry CLI to query, so Claude always hand-typed the `@vX` tag. |
| Cargo (`Cargo.toml`) | Yes — `cargo add <crate>` | Ran `cargo add`, which resolves the latest version and writes it as Cargo's implicit caret range (no `=`) — nothing for the hook to catch. |
| Bazel (`MODULE.bazel`) | No | There's no `bazel add`-style command that resolves a module's latest Bazel Central Registry release and writes it into `MODULE.bazel`; a `bazel_dep(name = ..., version = ...)` entry is always hand-typed. |

`go.mod`, `package.json`, and `Cargo.toml` are the manifests where the
ecosystem's own tooling already avoids the stale-pin problem.
However, `yul` still acts as a safety net for those ecosystems.

