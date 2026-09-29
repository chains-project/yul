import test from "node:test";
import assert from "node:assert/strict";
import { detectColorLevel, supportsColor, ColorLevel } from "../src/supports-color.js";

const tty = (depth) => ({ isTTY: true, getColorDepth: () => depth });
const pipe = { isTTY: false };

test("disables color for non-TTY streams", () => {
  assert.equal(detectColorLevel({ env: {}, stream: pipe }), ColorLevel.NONE);
});

test("detects truecolor from stream depth", () => {
  assert.equal(detectColorLevel({ env: {}, stream: tty(24) }), ColorLevel.TRUECOLOR);
  assert.equal(detectColorLevel({ env: {}, stream: tty(8) }), ColorLevel.COLORS_256);
  assert.equal(detectColorLevel({ env: {}, stream: tty(4) }), ColorLevel.BASIC);
  assert.equal(detectColorLevel({ env: {}, stream: tty(1) }), ColorLevel.NONE);
});

test("falls back to basic color for a plain TTY", () => {
  assert.equal(detectColorLevel({ env: {}, stream: { isTTY: true } }), ColorLevel.BASIC);
});

test("honors NO_COLOR when non-empty", () => {
  assert.equal(detectColorLevel({ env: { NO_COLOR: "1" }, stream: tty(24) }), ColorLevel.NONE);
});

test("ignores empty NO_COLOR", () => {
  assert.equal(detectColorLevel({ env: { NO_COLOR: "" }, stream: tty(24) }), ColorLevel.TRUECOLOR);
});

test("honors TERM=dumb", () => {
  assert.equal(detectColorLevel({ env: { TERM: "dumb" }, stream: tty(24) }), ColorLevel.NONE);
});

test("FORCE_COLOR overrides NO_COLOR and non-TTY", () => {
  assert.equal(
    detectColorLevel({ env: { FORCE_COLOR: "1", NO_COLOR: "1" }, stream: pipe }),
    ColorLevel.BASIC,
  );
  assert.equal(detectColorLevel({ env: { FORCE_COLOR: "3" }, stream: pipe }), ColorLevel.TRUECOLOR);
});

test("FORCE_COLOR=0 disables color on a TTY", () => {
  assert.equal(detectColorLevel({ env: { FORCE_COLOR: "0" }, stream: tty(24) }), ColorLevel.NONE);
});

test("FORCE_COLOR with an empty value means basic color", () => {
  assert.equal(detectColorLevel({ env: { FORCE_COLOR: "" }, stream: pipe }), ColorLevel.BASIC);
});

test("supportsColor checks the requested threshold", () => {
  assert.equal(supportsColor(2, { env: { FORCE_COLOR: "1" }, stream: pipe }), true);
  assert.equal(supportsColor(256, { env: { FORCE_COLOR: "1" }, stream: pipe }), false);
  assert.equal(supportsColor(256, { env: { FORCE_COLOR: "3" }, stream: pipe }), true);
});
