import { test } from "node:test";
import assert from "node:assert/strict";
import { rangeToRegex, rangeToRegexSource } from "../src/index.js";

function matches(re, value) {
  return new RegExp(re.source).test(String(value));
}

test("matches every integer in a range and nothing outside", () => {
  const cases = [
    [1, 100],
    [0, 9],
    [0, 10],
    [5, 12],
    [123, 4599],
    [-50, 50],
    [-100, -1],
    [-300, -150],
    [0, 0],
    [42, 42],
    [999, 1000],
    [1, 999999],
  ];

  for (const [min, max] of cases) {
    const re = rangeToRegex(`${min}-${max}`);

    const inside = new Set([min, max, Math.trunc((min + max) / 2)]);
    for (const n of inside) {
      assert.ok(matches(re, n), `${n} should match range ${min}-${max}`);
    }

    for (const n of [min - 1, max + 1, max + 1000, min - 1000]) {
      assert.ok(!matches(re, n), `${n} should not match range ${min}-${max}`);
    }
  }
});

test("rejects leading zeros and partial matches", () => {
  const re = rangeToRegex("1-100");
  assert.ok(matches(re, "1"));
  assert.ok(matches(re, "100"));
  assert.ok(!matches(re, "01"));
  assert.ok(!matches(re, "1000"));
  assert.ok(!matches(re, "1abc"));
  assert.ok(!matches(re, "abc"));
});

test("accepts (min, max) arguments and whitespace", () => {
  assert.equal(rangeToRegex(1, 100).source, rangeToRegex("1-100").source);
  assert.equal(rangeToRegex(" 1 - 100 ").source, rangeToRegex("1-100").source);
});

test("swaps reversed bounds", () => {
  assert.equal(rangeToRegex("100-1").source, rangeToRegex("1-100").source);
});

test("exposes the raw pattern source", () => {
  assert.equal(rangeToRegexSource(1, 100), rangeToRegex("1-100").source.slice(4, -2));
});

test("rejects malformed input", () => {
  assert.throws(() => rangeToRegex("nope"), TypeError);
  assert.throws(() => rangeToRegex("1-"), TypeError);
  assert.throws(() => rangeToRegex("a-b"), TypeError);
});
