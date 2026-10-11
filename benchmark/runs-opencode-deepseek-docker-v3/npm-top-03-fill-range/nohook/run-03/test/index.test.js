import assert from "node:assert/strict";
import { test } from "node:test";
import { expandRange } from "../index.js";

test("expands ascending numeric ranges", () => {
  assert.deepEqual(expandRange("1-10"), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test("expands descending numeric ranges", () => {
  assert.deepEqual(expandRange("3-1"), [3, 2, 1]);
});

test("expands single-value numeric ranges", () => {
  assert.deepEqual(expandRange("5-5"), [5]);
});

test("expands lowercase alphabetic ranges", () => {
  assert.deepEqual(expandRange("a-z"), "abcdefghijklmnopqrstuvwxyz".split(""));
});

test("expands uppercase alphabetic ranges", () => {
  assert.deepEqual(expandRange("X-Z"), ["X", "Y", "Z"]);
});

test("ignores surrounding whitespace", () => {
  assert.deepEqual(expandRange("  2-4  "), [2, 3, 4]);
});

test("rejects invalid input", () => {
  assert.throws(() => expandRange("1-a"), RangeError);
  assert.throws(() => expandRange("z-a1"), RangeError);
  assert.throws(() => expandRange(10), TypeError);
});
