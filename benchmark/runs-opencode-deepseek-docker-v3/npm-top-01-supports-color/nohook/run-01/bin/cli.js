#!/usr/bin/env node
import { detectColorLevel, ColorLevel } from "../src/color-support.js"
import { createColors } from "../src/colors.js"

const LEVEL_NAMES = {
  [ColorLevel.None]: "none",
  [ColorLevel.Basic]: "basic (16 colors)",
  [ColorLevel.Ansi256]: "ansi256",
  [ColorLevel.TrueColor]: "truecolor (16m)",
}

const args = new Set(process.argv.slice(2))
const json = args.has("--json")
const level = detectColorLevel()
const c = createColors(level)

if (json) {
  process.stdout.write(
    JSON.stringify({ level, supportsColor: level > ColorLevel.None }) + "\n",
  )
} else if (args.has("--demo")) {
  console.log(c.red("red"), c.green("green"), c.blue("blue"))
  console.log(c.ansi256(208, "ansi256"), c.rgb(255, 128, 0, "truecolor"))
  console.log(`level: ${c.bold(LEVEL_NAMES[level])}`)
} else {
  const status = c.supportsColor ? c.green("yes") : c.yellow("no")
  console.log(`Color support: ${status} (${LEVEL_NAMES[level]})`)
}
