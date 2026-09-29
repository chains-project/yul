import test from "node:test";
import assert from "node:assert/strict";
import { createColors } from "../src/colors.js";
import { ColorLevel } from "../src/supports-color.js";

test("formatters are identity functions when color is disabled", () => {
  const colors = createColors(ColorLevel.NONE);
  assert.equal(colors.enabled, false);
  assert.equal(colors.red("hi"), "hi");
  assert.equal(colors.rgb(255, 0, 0, "hi"), "hi");
  assert.equal(colors.ansi256(196, "hi"), "hi");
});

test("basic formatters wrap text in ANSI codes", () => {
  const colors = createColors(ColorLevel.BASIC);
  assert.equal(colors.red("hi"), "\u001b[31mhi\u001b[39m");
  assert.equal(colors.bold("hi"), "\u001b[1mhi\u001b[22m");
});

test("truecolor formatter requires level 3", () => {
  const basic = createColors(ColorLevel.BASIC);
  assert.equal(basic.rgb(255, 0, 0, "hi"), "hi");

  const truecolor = createColors(ColorLevel.TRUECOLOR);
  assert.equal(truecolor.rgb(255, 0, 0, "hi"), "\u001b[38;2;255;0;0mhi\u001b[39m");
});

test("ansi256 formatter requires at least level 2", () => {
  const basic = createColors(ColorLevel.BASIC);
  assert.equal(basic.ansi256(196, "hi"), "hi");

  const colors = createColors(ColorLevel.COLORS_256);
  assert.equal(colors.ansi256(196, "hi"), "\u001b[38;5;196mhi\u001b[39m");
});

test("empty strings are left untouched", () => {
  const colors = createColors(ColorLevel.TRUECOLOR);
  assert.equal(colors.red(""), "");
});
