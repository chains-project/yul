import test from "node:test";
import assert from "node:assert/strict";
import { expandRange } from "../src/expandRange.js";

test("expands an ascending numeric range", () => {
  assert.deepEqual(expandRange("1-5"), [1, 2, 3, 4, 5]);
});

test("expands a descending numeric range", () => {
  assert.deepEqual(expandRange("5-1"), [5, 4, 3, 2, 1]);
});

test("expands a single-element numeric range", () => {
  assert.deepEqual(expandRange("3-3"), [3]);
});

test("expands negative numbers", () => {
  assert.deepEqual(expandRange("-2-2"), [-2, -1, 0, 1, 2]);
});

test("expands a lowercase letter range", () => {
  assert.deepEqual(expandRange("a-e"), ["a", "b", "c", "d", "e"]);
});

test("expands an uppercase letter range", () => {
  assert.deepEqual(expandRange("X-Z"), ["X", "Y", "Z"]);
});

test("tolerates surrounding whitespace", () => {
  assert.deepEqual(expandRange(" 1 - 3 "), [1, 2, 3]);
});

test("rejects mixed-case letter ranges", () => {
  assert.throws(() => expandRange("a-Z"), /same letter case/);
});

test("rejects invalid input", () => {
  assert.throws(() => expandRange("hello"), /Invalid range/);
  assert.throws(() => expandRange(""), /must not be empty/);
  assert.throws(() => expandRange(5), /must be a string/);
});
