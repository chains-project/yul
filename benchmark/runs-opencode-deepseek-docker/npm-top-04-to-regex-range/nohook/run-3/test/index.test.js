import test from "node:test";
import assert from "node:assert/strict";
import {
  rangeToRegex,
  rangeRegExp,
  parseRange,
  rangeStringToRegex,
  rangeStringToRegExp,
} from "../src/index.js";

function assertRangeMatches(min, max, options = {}) {
  const re = rangeRegExp(min, max, options);
  for (let n = min; n <= max; n++) {
    assert.equal(re.test(String(n)), true, `expected ${n} to match ${re}`);
  }
  for (const outside of [min - 1, max + 1, max + 10, min - 100]) {
    if (outside < 0) continue;
    assert.equal(re.test(String(outside)), false, `expected ${outside} NOT to match ${re}`);
  }
}

test("examples", () => {
  assert.equal(rangeStringToRegex("1-100"), "[1-9]|[1-9]\\d|100");
  assert.equal(rangeStringToRegex("1-9"), "[1-9]");
  assert.equal(
    rangeStringToRegex("0-255"),
    "\\d|[1-9]\\d|(?:1\\d{2}|2(?:0\\d|[1-4]\\d|5[0-5]))",
  );
});

test("single digit range", () => {
  assert.equal(rangeToRegex(3, 7), "[3-7]");
  assert.equal(rangeToRegex(5, 5), "5");
});

test("fixed width ranges", () => {
  assert.equal(rangeToRegex(10, 99), "[1-9]\\d");
  assert.equal(rangeToRegex(200, 599), "[2-5]\\d{2}");
  assert.equal(rangeToRegex(1000, 9999), "[1-9]\\d{3}");
  assert.equal(rangeToRegex(1050, 1059), "105\\d");
});

test("parseRange", () => {
  assert.deepEqual(parseRange("1-100"), { min: 1, max: 100 });
  assert.deepEqual(parseRange(" 42 - 99 "), { min: 42, max: 99 });
  assert.deepEqual(parseRange(7), { min: 7, max: 7 });
  assert.throws(() => parseRange("nope"));
});

test("brute force correctness across many ranges", () => {
  const cases = [
    [0, 0],
    [0, 9],
    [0, 10],
    [1, 100],
    [1, 255],
    [0, 255],
    [7, 7],
    [42, 42],
    [12, 3456],
    [99, 100],
    [100, 999],
    [100, 1000],
    [123, 4567],
    [500, 12345],
    [9998, 10002],
    [1, 100000],
  ];
  for (const [min, max] of cases) {
    assertRangeMatches(min, max);
  }
});

test("padded ranges accept leading zeros", () => {
  const re = rangeStringToRegExp("1-100", { pad: true });
  for (const n of ["1", "01", "001", "99", "099", "100"]) {
    assert.equal(re.test(n), true, `expected ${n} to match`);
  }
  assert.equal(re.test("101"), false);
  assert.equal(re.test("0001"), false);
});

test("non-anchored mode finds numbers inside text", () => {
  const re = rangeStringToRegExp("1-100", { anchors: false });
  assert.equal(re.test("item 42"), true);
  assert.equal(re.test("item 420"), true);
  const anchored = rangeStringToRegExp("1-100");
  assert.equal(anchored.test("item 42"), false);
});

test("scaling to large ranges stays compact", () => {
  const pattern = rangeToRegex(0, 1000000);
  assert.ok(pattern.length < 200, `pattern unexpectedly long: ${pattern.length}`);
  assertRangeMatches(0, 1000);
});

test("invalid input is rejected", () => {
  assert.throws(() => rangeToRegex(-1, 10), RangeError);
  assert.throws(() => rangeToRegex(0, Infinity), TypeError);
});
