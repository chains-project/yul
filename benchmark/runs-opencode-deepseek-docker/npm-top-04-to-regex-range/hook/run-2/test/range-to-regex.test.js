import assert from "node:assert/strict";
import test from "node:test";
import {
  parseRange,
  rangeStringToRegex,
  rangeToRegex,
  rangeToRegexSource,
} from "../src/range-to-regex.js";

/** Assert the regex accepts exactly the integers in [min, max]. */
function assertMatchesRange(min, max, probes) {
  const regex = rangeToRegex(min, max);
  for (const value of probes) {
    const expected = value >= min && value <= max;
    assert.equal(
      regex.test(String(value)),
      expected,
      `${regex} should ${expected ? "" : "not "}match ${value} (range ${min}-${max})`,
    );
  }
}

test("parses range strings", () => {
  assert.deepEqual(parseRange("1-100"), [1, 100]);
  assert.deepEqual(parseRange(" 5 - 10 "), [5, 10]);
  assert.deepEqual(parseRange("42"), [42, 42]);
  assert.deepEqual(parseRange("100-1"), [1, 100]);
});

test("rejects malformed ranges", () => {
  for (const bad of ["", "abc", "1-", "-5", "1.5-2", "1..2"]) {
    assert.throws(() => parseRange(bad), SyntaxError, `should reject "${bad}"`);
  }
});

test("rejects invalid bounds", () => {
  assert.throws(() => rangeToRegex(-1, 10), RangeError);
  assert.throws(() => rangeToRegex(1.5, 10), TypeError);
});

test("canonical examples", () => {
  assert.equal(rangeToRegexSource(1, 100), "[1-9]|[1-9][0-9]|100");
  assert.equal(rangeStringToRegex("1-100").toString(), "/^(?:[1-9]|[1-9][0-9]|100)$/");
  assert.equal(rangeToRegexSource(0, 9), "[0-9]");
  assert.equal(rangeToRegexSource(5, 5), "5");
});

test("exhaustively checks small ranges", () => {
  const probes = [];
  for (let value = 0; value <= 260; value++) probes.push(value);
  for (let min = 0; min <= 120; min++) {
    for (let max = min; max <= 120; max++) {
      assertMatchesRange(min, max, probes);
    }
  }
});

test("checks larger and awkward ranges", () => {
  const cases = [
    [0, 1000],
    [1, 65535],
    [100, 1000],
    [500, 5000],
    [123, 4567],
    [999, 1001],
    [10, 99],
    [100, 999],
    [1000, 9999],
    [12345, 98765],
    [7, 1499],
    [250, 250],
  ];
  for (const [min, max] of cases) {
    const probes = [];
    for (let value = Math.max(0, min - 5); value <= max + 5; value++) {
      probes.push(value);
    }
    probes.push(0, 100000, 999999);
    assertMatchesRange(min, max, probes);
  }
});

test("does not match leading zeros", () => {
  const regex = rangeToRegex(0, 100);
  assert.equal(regex.test("007"), false);
  assert.equal(regex.test("00"), false);
  assert.equal(regex.test("0"), true);
});

test("supports regex flags", () => {
  const regex = rangeToRegex(1, 10, "g");
  assert.equal(regex.flags, "g");
  assert.ok(regex instanceof RegExp);
});
