import test from "node:test";
import assert from "node:assert/strict";
import { expandRange } from "../src/expand-range.js";

test("expands an ascending numeric range", () => {
  assert.deepEqual(expandRange("1-10"), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test("expands a descending numeric range", () => {
  assert.deepEqual(expandRange("5-1"), [5, 4, 3, 2, 1]);
});

test("expands an ascending alpha range", () => {
  assert.deepEqual(expandRange("a-e"), ["a", "b", "c", "d", "e"]);
});

test("expands a descending alpha range", () => {
  assert.deepEqual(expandRange("z-v"), ["z", "y", "x", "w", "v"]);
});

test("handles single-value ranges", () => {
  assert.deepEqual(expandRange("4-4"), [4]);
  assert.deepEqual(expandRange("m-m"), ["m"]);
});

test("rejects malformed ranges", () => {
  assert.throws(() => expandRange("1-"), /Invalid range/);
  assert.throws(() => expandRange("a-z-1"), /Invalid range/);
  assert.throws(() => expandRange("1-a"), /Invalid range/);
});

test("rejects non-string input", () => {
  assert.throws(() => expandRange(10), TypeError);
});
