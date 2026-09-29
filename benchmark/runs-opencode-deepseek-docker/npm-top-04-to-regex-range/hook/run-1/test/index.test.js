import test from "node:test";
import assert from "node:assert/strict";
import { rangeToRegex, parseRange, matches } from "../index.js";

test("parseRange understands 'min-max' strings", () => {
  assert.deepEqual(parseRange("1-100"), [1, 100]);
  assert.deepEqual(parseRange(" 5 - 10 "), [5, 10]);
  assert.deepEqual(parseRange("0-0"), [0, 0]);
  assert.throws(() => parseRange("abc"), /invalid numeric range/);
  assert.throws(() => parseRange("1..100"), /invalid numeric range/);
});

test("the canonical 1-100 example", () => {
  const source = rangeToRegex(1, 100);
  const regex = new RegExp(source);
  for (const n of [1, 9, 10, 42, 99, 100]) {
    assert.ok(regex.test(String(n)), `${n} should match ${source}`);
  }
  for (const n of [0, 101, 1000]) {
    assert.ok(!regex.test(String(n)), `${n} should not match ${source}`);
  }
  assert.equal(matches("1-100", 100), true);
  assert.equal(matches("1-100", 0), false);
});

test("anchoring can be disabled", () => {
  const anchored = rangeToRegex(1, 9);
  const loose = rangeToRegex(1, 9, { anchor: false });
  assert.ok(anchored.startsWith("^"));
  assert.ok(anchored.endsWith("$"));
  assert.equal(anchored, `^(?:${loose})$`);
});

test("inputs may be swapped and reject negatives", () => {
  assert.equal(rangeToRegex(100, 1), rangeToRegex(1, 100));
  assert.throws(() => rangeToRegex(-1, 10), /non-negative/);
  assert.throws(() => rangeToRegex(1.5, 10), /integer/);
});

test("matches every integer in every small range", () => {
  const limit = 100;
  const checkTo = 130;
  for (let min = 0; min <= limit; min++) {
    for (let max = min; max <= limit; max++) {
      const source = rangeToRegex(min, max, { anchor: true });
      const regex = new RegExp(source);
      for (let value = 0; value <= checkTo; value++) {
        const expected = value >= min && value <= max;
        assert.equal(
          regex.test(String(value)),
          expected,
          `range ${min}-${max}: ${value} against ${source}`,
        );
      }
    }
  }
});

test("handles wide ranges that cross digit-length boundaries", () => {
  const cases = [
    [0, 9],
    [0, 10],
    [9, 11],
    [5, 9999],
    [100, 999],
    [123, 4567],
    [98, 102],
    [1000, 1000],
  ];
  for (const [min, max] of cases) {
    const regex = new RegExp(rangeToRegex(min, max));
    const samples = [min, max, min - 1, max + 1, Math.floor((min + max) / 2)].filter(
      (n) => n >= 0,
    );
    for (const value of samples) {
      assert.equal(
        regex.test(String(value)),
        value >= min && value <= max,
        `range ${min}-${max}: ${value} against ${rangeToRegex(min, max)}`,
      );
    }
  }
});
