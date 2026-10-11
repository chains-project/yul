const AUTH_STORE_RE = /\.local[/\\]share[/\\]opencode[/\\]auth\.json|opencode[/\\]auth\.json/i

function mentionsAuthStore(args) {
  if (typeof args === "string") return AUTH_STORE_RE.test(args)
  if (Array.isArray(args)) return args.some(mentionsAuthStore)
  if (args && typeof args === "object") return Object.values(args).some(mentionsAuthStore)
  return false
}

export const YulAuthGuardPlugin = async () => {
  return {
    "tool.execute.before": async (_input, output) => {
      if (mentionsAuthStore(output.args)) {
        throw new Error("yul: reading OpenCode's credential store is not permitted")
      }
    },
  }
}
