export const ColorLevel = {
  None: 0,
  Basic: 1,
  Ansi256: 2,
  TrueColor: 3,
}

function hasFlag(name, env) {
  return Object.prototype.hasOwnProperty.call(env, name)
}

function parseForceColor(env) {
  if (!hasFlag("FORCE_COLOR", env)) return undefined
  const value = env.FORCE_COLOR
  if (value === "false" || value === "0") return ColorLevel.None
  if (value === "true" || value === "") return ColorLevel.Basic
  if (value === "2") return ColorLevel.Ansi256
  if (value === "3") return ColorLevel.TrueColor
  return ColorLevel.Basic
}

export function detectColorLevel({
  env = process.env,
  isTTY = Boolean(process.stdout && process.stdout.isTTY),
  platform = process.platform,
} = {}) {
  const forced = parseForceColor(env)
  if (forced !== undefined) return forced

  if (hasFlag("NO_COLOR", env)) return ColorLevel.None
  if (env.TERM === "dumb") return ColorLevel.None

  if (env.COLORTERM === "truecolor" || env.COLORTERM === "24bit") {
    return ColorLevel.TrueColor
  }

  if (env.TERM_PROGRAM === "iTerm.app" && /^3/.test(env.TERM_PROGRAM_VERSION || "")) {
    return ColorLevel.TrueColor
  }

  if (/(?:-|\b)(?:256|16m)color\b/i.test(env.TERM || "")) {
    return ColorLevel.Ansi256
  }

  if (isTTY) return ColorLevel.Basic
  if (platform === "win32" && env.ANSICON) return ColorLevel.Basic
  if (platform === "win32" && /^9/.test(env.ConEmuANSI || "")) return ColorLevel.Basic

  return ColorLevel.None
}

export function supportsColor(options) {
  return detectColorLevel(options) > ColorLevel.None
}
