import test from "node:test"
import assert from "node:assert/strict"
import { expandRange } from "../src/expand-range.js"

test("expands ascending integer ranges", () => {
  assert.deepEqual(expandRange("1-5"), [1, 2, 3, 4, 5])
})

test("expands descending integer ranges", () => {
  assert.deepEqual(expandRange("5-1"), [5, 4, 3, 2, 1])
})

test("includes negative numbers", () => {
  assert.deepEqual(expandRange("-3-1"), [-3, -2, -1, 0, 1])
})

test("applies a numeric step", () => {
  assert.deepEqual(expandRange("1-10", 2), [1, 3, 5, 7, 9])
})

test("expands lowercase and uppercase letter ranges", () => {
  assert.deepEqual(expandRange("a-e"), ["a", "b", "c", "d", "e"])
  assert.deepEqual(expandRange("E-A"), ["E", "D", "C", "B", "A"])
})

test("trims surrounding whitespace", () => {
  assert.deepEqual(expandRange(" 3 - 5 "), [3, 4, 5])
})

test("rejects malformed or mismatched ranges", () => {
  assert.throws(() => expandRange("abc"))
  assert.throws(() => expandRange("a-5"))
  assert.throws(() => expandRange("A-z"))
  assert.throws(() => expandRange("1-5", 0))
})
