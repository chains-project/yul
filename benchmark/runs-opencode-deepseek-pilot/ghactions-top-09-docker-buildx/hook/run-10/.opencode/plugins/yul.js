// Manifest basenames yul knows how to check, mirroring pkg/*'s Filename()
// values (githubactions workflows use MatchesPath instead of a fixed name,
// so they're matched separately below).
const MANIFEST_RE = /(^|[/\\ '"=])(pom\.xml|requirements\.txt|pyproject\.toml|package\.json|go\.mod|Cargo\.toml|\.github\/workflows\/[^\s'"]+\.ya?ml)(?=[/\\ '"]|$)/
// Shell constructs that mutate a file's *content* on disk - not an
// exhaustive parse of bash, just enough to catch the bypass a live model
// actually used (`printf ... > requirements.txt`) plus its common cousins.
const WRITE_RE = />>?(?!&)|\btee\b|\bsed\s+-i|\bperl\s+-i|\bdd\s+of=|\bcp\s|\bmv\s/

export const YulPlugin = async () => {
  const YUL_BIN = process.env.YUL_BIN || "yul"
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "bash") {
        const cmd = output.args.command || ""
        if (MANIFEST_RE.test(cmd) && WRITE_RE.test(cmd)) {
          throw new Error(
            "yul: use the write or edit tool to modify dependency manifests, not bash " +
            "(bash writes bypass the outdated-dependency check)"
          )
        }
        return
      }
      if (input.tool !== "write" && input.tool !== "edit") return
      const a = output.args
      const payload = input.tool === "write"
        ? { tool_name: "Write", tool_input: { file_path: a.filePath, content: a.content } }
        : {
            tool_name: "Edit",
            tool_input: {
              file_path: a.filePath,
              old_string: a.oldString,
              new_string: a.newString,
              replace_all: !!a.replaceAll,
            },
          }

      const proc = Bun.spawn([YUL_BIN], { stdin: "pipe", stdout: "pipe", stderr: "pipe" })
      proc.stdin.write(JSON.stringify(payload))
      proc.stdin.end()
      const [code, stderr] = await Promise.all([proc.exited, new Response(proc.stderr).text()])
      if (code === 2) throw new Error(stderr.trim() || "yul: blocked outdated dependency")
    },
  }
}
