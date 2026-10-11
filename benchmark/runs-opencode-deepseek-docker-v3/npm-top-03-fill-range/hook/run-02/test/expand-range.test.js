import test from "node:test";
import assert from "node:assert/strict";
import { expandRange } from "../src/expand-range.js";

test("expands an ascending numeric range", () => {
  assert.deepEqual(expandRange("1-5"), [1, 2, 3, 4, 5]);
});

test("expands a descending numeric range", () => {
  assert.deepEqual(expandRange("5-1"), [5, 4, 3, 2, 1]);
});

test("expands negative numeric ranges", () => {
  assert.deepEqual(expandRange("-3-1"), [-3, -2, -1, 0, 1]);
});

test("expands an ascending letter range", () => {
  assert.deepEqual(expandRange("a-e"), ["a", "b", "c", "d", "e"]);
});

test("expands a descending letter range", () => {
  assert.deepEqual(expandRange("e-a"), ["e", "d", "c", "b", "a"]);
});

test("expands a single-value range", () => {
  assert.deepEqual(expandRange("7-7"), [7]);
});

test("ignores surrounding whitespace", () => {
  assert.deepEqual(expandRange("  2-4  "), [2, 3, 4]);
});

test("rejects malformed ranges", () => {
  assert.throws(() => expandRange("abc"), /Invalid range/);
  assert.throws(() => expandRange("1-a"), /both/);
  assert.throws(() => expandRange(10), /string/);
});
