import { test } from "node:test";
import assert from "node:assert/strict";
import { expandRange } from "../src/range.js";

test("expands an ascending numeric range", () => {
  assert.deepEqual(expandRange("1-10"), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test("expands a descending numeric range", () => {
  assert.deepEqual(expandRange("3-1"), [3, 2, 1]);
});

test("expands a numeric range with a step", () => {
  assert.deepEqual(expandRange("0-10:2"), [0, 2, 4, 6, 8, 10]);
});

test("expands a lowercase letter range", () => {
  assert.deepEqual(expandRange("a-e"), ["a", "b", "c", "d", "e"]);
});

test("expands an uppercase letter range", () => {
  assert.deepEqual(expandRange("X-Z"), ["X", "Y", "Z"]);
});

test("expands a descending letter range", () => {
  assert.deepEqual(expandRange("c-a"), ["c", "b", "a"]);
});

test("throws on malformed input", () => {
  assert.throws(() => expandRange("abc"), /Invalid range/);
  assert.throws(() => expandRange("a-1"), /Invalid range/);
});

test("throws on a non-positive or non-integer step", () => {
  assert.throws(() => expandRange("1-10:0"), RangeError);
  assert.throws(() => expandRange("1-10:x"), RangeError);
});

test("throws on a non-string argument", () => {
  assert.throws(() => expandRange(5), TypeError);
});
