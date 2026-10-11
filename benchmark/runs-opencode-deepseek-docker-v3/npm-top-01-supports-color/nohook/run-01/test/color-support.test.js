import { test } from "node:test"
import assert from "node:assert/strict"
import { ColorLevel, detectColorLevel, supportsColor } from "../src/color-support.js"

test("NO_COLOR disables color", () => {
  assert.equal(detectColorLevel({ env: { NO_COLOR: "1" }, isTTY: true }), ColorLevel.None)
})

test("FORCE_COLOR overrides NO_COLOR and non-tty", () => {
  assert.equal(
    detectColorLevel({ env: { FORCE_COLOR: "1", NO_COLOR: "1" }, isTTY: false }),
    ColorLevel.Basic,
  )
})

test("FORCE_COLOR levels map to color depth", () => {
  assert.equal(detectColorLevel({ env: { FORCE_COLOR: "0" } }), ColorLevel.None)
  assert.equal(detectColorLevel({ env: { FORCE_COLOR: "2" } }), ColorLevel.Ansi256)
  assert.equal(detectColorLevel({ env: { FORCE_COLOR: "3" } }), ColorLevel.TrueColor)
})

test("TERM=dumb disables color", () => {
  assert.equal(detectColorLevel({ env: { TERM: "dumb" }, isTTY: true }), ColorLevel.None)
})

test("COLORTERM=truecolor enables truecolor", () => {
  assert.equal(
    detectColorLevel({ env: { COLORTERM: "truecolor" }, isTTY: true }),
    ColorLevel.TrueColor,
  )
})

test("256color TERM maps to ansi256", () => {
  assert.equal(
    detectColorLevel({ env: { TERM: "xterm-256color" }, isTTY: true }),
    ColorLevel.Ansi256,
  )
})

test("plain TTY gets basic color", () => {
  assert.equal(detectColorLevel({ env: { TERM: "xterm" }, isTTY: true }), ColorLevel.Basic)
})

test("non-tty without hints gets no color", () => {
  assert.equal(detectColorLevel({ env: {}, isTTY: false }), ColorLevel.None)
})

test("supportsColor is a boolean shortcut", () => {
  assert.equal(supportsColor({ env: { FORCE_COLOR: "1" }, isTTY: false }), true)
  assert.equal(supportsColor({ env: {}, isTTY: false }), false)
})
