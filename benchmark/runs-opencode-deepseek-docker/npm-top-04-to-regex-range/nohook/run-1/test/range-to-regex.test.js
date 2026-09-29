import test from "node:test";
import assert from "node:assert/strict";
import {
  parseRange,
  rangeToRegex,
  rangeToRegexFromString,
} from "../src/range-to-regex.js";

const compile = (min, max) => new RegExp(rangeToRegex(min, max));
const accepts = (regex, value) => regex.test(String(value));

test("matches the canonical 1-100 example", () => {
  const regex = compile(1, 100);

  for (let value = 1; value <= 100; value += 1) {
    assert.equal(accepts(regex, value), true, `${value} should match`);
  }

  for (const value of ["0", "101", "1000", "007", "-5", "1a", ""]) {
    assert.equal(accepts(regex, value), false, `"${value}" should not match`);
  }
});

test("supports single value and single digit ranges", () => {
  const single = compile(42, 42);
  assert.equal(accepts(single, 42), true);
  assert.equal(accepts(single, 41), false);
  assert.equal(accepts(single, 421), false);

  const digits = compile(3, 8);
  for (let value = 0; value <= 20; value += 1) {
    assert.equal(accepts(digits, value), value >= 3 && value <= 8);
  }
});

test("brute-force verifies every sub-range in a small window", () => {
  for (let min = 0; min <= 25; min += 1) {
    for (let max = min; max <= 25; max += 1) {
      const regex = compile(min, max);
      const label = `range ${min}-${max}`;

      for (let value = 0; value <= 120; value += 1) {
        assert.equal(
          accepts(regex, value),
          value >= min && value <= max,
          `${label} with value ${value}`,
        );
      }
    }
  }
});

test("rejects leading zeros for multi-digit ranges", () => {
  const regex = compile(10, 999);
  for (const value of ["010", "099", "007"]) {
    assert.equal(accepts(regex, value), false, `"${value}" should not match`);
  }
});

test("handles ranges larger than Number.MAX_SAFE_INTEGER", () => {
  const regex = compile("9007199254740990", "9007199254740995");
  for (const value of [
    "9007199254740989",
    "9007199254740990",
    "9007199254740993",
    "9007199254740995",
    "9007199254740996",
  ]) {
    assert.equal(
      accepts(regex, value),
      value >= "9007199254740990" && value <= "9007199254740995",
      value,
    );
  }
});

test("anchoring can be disabled", () => {
  const anchored = new RegExp(rangeToRegex(1, 100));
  const unanchored = new RegExp(rangeToRegex(1, 100, { anchors: false }));

  assert.equal(anchored.test("abc42xyz"), false);
  assert.equal(unanchored.test("abc42xyz"), true);
  assert.equal(rangeToRegex(1, 100, { anchors: false }).startsWith("^"), false);
});

test("parseRange extracts bounds and rejects malformed input", () => {
  assert.deepEqual(parseRange("1-100"), ["1", "100"]);
  assert.deepEqual(parseRange(" 7 - 9 "), ["7", "9"]);
  assert.equal(rangeToRegexFromString("1-100"), rangeToRegex(1, 100));

  assert.throws(() => parseRange("abc"), RangeError);
  assert.throws(() => parseRange("100"), RangeError);
  assert.throws(() => rangeToRegex(10, 1), RangeError);
  assert.throws(() => rangeToRegex(-1, 5), RangeError);
});
