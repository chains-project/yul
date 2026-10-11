import { test } from "node:test";
import assert from "node:assert/strict";
import { expandRange } from "../src/index.js";

test("expands positive integer ranges", () => {
  assert.deepEqual(expandRange("1-10"), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test("expands single digit ranges", () => {
  assert.deepEqual(expandRange("3-6"), [3, 4, 5, 6]);
});

test("expands descending integer ranges", () => {
  assert.deepEqual(expandRange("10-1"), [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]);
});

test("expands negative integer ranges", () => {
  assert.deepEqual(expandRange("-3-2"), [-3, -2, -1, 0, 1, 2]);
});

test("expands lowercase letter ranges", () => {
  assert.deepEqual(expandRange("a-z"), "abcdefghijklmnopqrstuvwxyz".split(""));
});

test("expands uppercase letter ranges", () => {
  assert.deepEqual(expandRange("A-E"), ["A", "B", "C", "D", "E"]);
});

test("ignores surrounding whitespace", () => {
  assert.deepEqual(expandRange(" 1 - 3 "), [1, 2, 3]);
});

test("treats a lone value as a single element", () => {
  assert.deepEqual(expandRange("7"), [7]);
  assert.deepEqual(expandRange("q"), ["q"]);
});

test("throws on invalid ranges", () => {
  assert.throws(() => expandRange("1-x"), SyntaxError);
  assert.throws(() => expandRange("foo"), SyntaxError);
  assert.throws(() => expandRange(""), SyntaxError);
});

test("throws on non-string input", () => {
  assert.throws(() => expandRange(42), TypeError);
});
