import assert from "node:assert/strict";
import { test } from "node:test";
import { createPainter, supportsColor } from "../lib/colors.js";

const tty = (hasColors) => ({ isTTY: true, hasColors });

test("disables color when NO_COLOR is set", () => {
  assert.equal(supportsColor(tty(() => true), { NO_COLOR: "1" }), false);
  assert.equal(createPainter({ stream: tty(() => true), env: { NO_COLOR: "1" } }).green("x"), "x");
});

test("FORCE_COLOR overrides a non-tty stream", () => {
  assert.equal(supportsColor({ isTTY: false }, { FORCE_COLOR: "1" }), true);
});

test("FORCE_COLOR=0 disables color", () => {
  assert.equal(supportsColor(tty(() => true), { FORCE_COLOR: "0" }), false);
});

test("uses stream.hasColors when available", () => {
  assert.equal(supportsColor(tty(() => true), {}), true);
  assert.equal(supportsColor(tty(() => false), {}), false);
});

test("wraps text in ANSI codes when enabled", () => {
  const c = createPainter({ stream: tty(() => true), env: {} });
  assert.equal(c.green("ok"), "\u001b[32mok\u001b[39m");
});
