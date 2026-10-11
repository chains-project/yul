import { test } from "node:test";
import assert from "node:assert/strict";
import { expandRange } from "../src/index.js";

test("expands an ascending numeric range", () => {
  assert.deepEqual(expandRange("1-5"), [1, 2, 3, 4, 5]);
});

test("expands a descending numeric range", () => {
  assert.deepEqual(expandRange("5-1"), [5, 4, 3, 2, 1]);
});

test("expands a single-character alpha range", () => {
  assert.deepEqual(expandRange("a-e"), ["a", "b", "c", "d", "e"]);
});

test("expands a descending alpha range", () => {
  assert.deepEqual(expandRange("e-a"), ["e", "d", "c", "b", "a"]);
});

test("supports negative numbers", () => {
  assert.deepEqual(expandRange("-2-2"), [-2, -1, 0, 1, 2]);
});

test("supports multiple comma-separated ranges", () => {
  assert.deepEqual(expandRange("1-3,7-9"), [1, 2, 3, 7, 8, 9]);
});

test("honors a custom step", () => {
  assert.deepEqual(expandRange("0-10", { step: 5 }), [0, 5, 10]);
});

test("rejects invalid input", () => {
  assert.throws(() => expandRange("abc"), /Invalid range/);
  assert.throws(() => expandRange("1..5"), /Invalid range/);
});

test("enforces max size", () => {
  assert.throws(() => expandRange("1-100", { maxSize: 10 }), /max/);
});
