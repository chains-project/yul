# yul

A Claude Code `PreToolUse` hook that keeps Maven dependencies current. When Claude writes a `pom.xml`, the hook checks any newly added/changed dependency against Maven Central and blocks the write (exit 2) if it's pinned to an outdated version, so Claude sees the correct version on stderr and retries. Other files and untouched dependencies pass through untouched; resolver/network errors fail open.

## Usage

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "go run github.com/chains-project/yul@latest",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

Requires Go to be installed. No other setup needed.

### Example

Claude tries to write a `pom.xml` pinning `org.json:json` to `20240303`. The hook blocks it:

```
outdated dependencies, use these versions instead:
  org.json:json  20240303 -> 20260522
```

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
    "command":"go run github.com/chains-project/yul@latest",
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

Claude reads this from stderr and rewrites the manifest with the correct version.
