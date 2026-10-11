import { ColorLevel, detectColorLevel } from "./color-support.js"

const CODES = {
  reset: 0,
  bold: 1,
  red: 31,
  green: 32,
  yellow: 33,
  blue: 34,
  magenta: 35,
  cyan: 36,
  gray: 90,
}

function wrap(code, text) {
  return `\u001B[${code}m${text}\u001B[0m`
}

export function createColors(level = detectColorLevel()) {
  const colors = {}

  for (const [name, code] of Object.entries(CODES)) {
    colors[name] =
      level > ColorLevel.None
        ? (text) => wrap(code, String(text))
        : (text) => String(text)
  }

  if (level >= ColorLevel.Ansi256) {
    colors.ansi256 = (code, text) => wrap(`38;5;${code}`, String(text))
  } else {
    colors.ansi256 = (code, text) => String(text)
  }

  if (level >= ColorLevel.TrueColor) {
    colors.rgb = (r, g, b, text) => wrap(`38;2;${r};${g};${b}`, String(text))
  } else {
    colors.rgb = (r, g, b, text) => String(text)
  }

  colors.level = level
  colors.supportsColor = level > ColorLevel.None

  return colors
}
