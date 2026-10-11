import { test } from "node:test";
import assert from "node:assert/strict";
import { expandRange } from "../index.js";

test("expands ascending numeric ranges", () => {
  assert.deepEqual(expandRange("1-5"), [1, 2, 3, 4, 5]);
  assert.deepEqual(expandRange("1-10"), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test("expands descending numeric ranges", () => {
  assert.deepEqual(expandRange("5-1"), [5, 4, 3, 2, 1]);
});

test("expands multi-digit numeric ranges", () => {
  assert.deepEqual(expandRange("8-12"), [8, 9, 10, 11, 12]);
});

test("expands lowercase letter ranges", () => {
  assert.deepEqual(expandRange("a-e"), ["a", "b", "c", "d", "e"]);
  assert.deepEqual(expandRange("a-z").length, 26);
});

test("expands uppercase letter ranges", () => {
  assert.deepEqual(expandRange("A-C"), ["A", "B", "C"]);
});

test("expands descending letter ranges", () => {
  assert.deepEqual(expandRange("e-a"), ["e", "d", "c", "b", "a"]);
});

test("a single value expands to itself", () => {
  assert.deepEqual(expandRange("3-3"), [3]);
  assert.deepEqual(expandRange("c-c"), ["c"]);
});

test("tolerates surrounding whitespace", () => {
  assert.deepEqual(expandRange(" 1 - 3 "), [1, 2, 3]);
});

test("rejects mixed-case letter ranges", () => {
  assert.throws(() => expandRange("a-Z"), /same case/);
});

test("rejects malformed input", () => {
  assert.throws(() => expandRange("1:"), /invalid range/);
  assert.throws(() => expandRange("abc"), /invalid range/);
  assert.throws(() => expandRange("a-1"), /unsupported range/);
  assert.throws(() => expandRange(42), /must be a string/);
});
