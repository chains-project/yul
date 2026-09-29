import assert from "node:assert/strict";
import test from "node:test";

import { parseRange, rangeToRegex, rangeToRegexSource } from "../src/index.js";

function verify(min, max) {
  const regex = rangeToRegex(min, max);
  const candidates = new Set([
    0,
    1,
    2,
    min,
    max,
    max + 1,
    max + 2,
    max + 3,
    Math.floor((min + max) / 2),
  ]);

  for (let delta = -2; delta <= 2; delta += 1) {
    candidates.add(min + delta);
    candidates.add(max + delta);
  }

  if (max <= 5000) {
    for (let value = 0; value <= max + 3; value += 1) candidates.add(value);
  }

  for (const value of candidates) {
    if (value < 0) continue;
    const expected = value >= min && value <= max;
    assert.equal(
      regex.test(String(value)),
      expected,
      `${regex} should${expected ? "" : " not"} match ${value}`
    );
  }

  for (const padded of ["00", "01", "007", `0${min}`]) {
    assert.equal(regex.test(padded), false, `${regex} should not match ${padded}`);
  }
}

test("matches a range within a single digit length", () => {
  verify(1, 9);
  verify(3, 7);
  verify(5, 5);
  verify(0, 9);
});

test("matches a range spanning multiple digit lengths", () => {
  verify(1, 100);
  verify(1, 1000);
  verify(0, 100);
  verify(98, 102);
  verify(123, 456);
  verify(1000, 9999);
});

test("handles large boundaries", () => {
  verify(123456789, 123456999);
  verify(999999999, 1000000001);
});

test("generates expected source for 1-100", () => {
  assert.equal(
    rangeToRegexSource(1, 100),
    "(?:(?:1|[2-8]|9)|(?:1\\d|[2-8]\\d|9\\d)|100)"
  );
});

test("rejects invalid input", () => {
  assert.throws(() => rangeToRegexSource(10, 1), RangeError);
  assert.throws(() => rangeToRegexSource(-1, 5), RangeError);
  assert.throws(() => rangeToRegexSource(0.5, 5), TypeError);
  assert.throws(() => parseRange("abc"), SyntaxError);
  assert.throws(() => parseRange("1"), SyntaxError);
});

test("parses range expressions", () => {
  assert.deepEqual(parseRange("1-100"), [1, 100]);
  assert.deepEqual(parseRange(" 5 - 10 "), [5, 10]);
});
