import test from 'node:test';
import assert from 'node:assert/strict';

import { expandRange } from '../src/expandRange.js';

test('expands an ascending numeric range', () => {
  assert.deepEqual(expandRange('1-10'), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test('expands a descending numeric range', () => {
  assert.deepEqual(expandRange('5-1'), [5, 4, 3, 2, 1]);
});

test('expands negative numeric ranges', () => {
  assert.deepEqual(expandRange('-3-2'), [-3, -2, -1, 0, 1, 2]);
});

test('expands a lowercase alphabetic range', () => {
  assert.deepEqual(expandRange('a-z'), 'abcdefghijklmnopqrstuvwxyz'.split(''));
});

test('expands an uppercase alphabetic range', () => {
  assert.deepEqual(expandRange('A-C'), ['A', 'B', 'C']);
});

test('expands a reversed alphabetic range', () => {
  assert.deepEqual(expandRange('e-a'), ['e', 'd', 'c', 'b', 'a']);
});

test('wraps single values in an array', () => {
  assert.deepEqual(expandRange('5'), [5]);
  assert.deepEqual(expandRange('c'), ['c']);
});

test('trims surrounding whitespace', () => {
  assert.deepEqual(expandRange('  2-4  '), [2, 3, 4]);
});

test('rejects mixed-case alphabetic ranges', () => {
  assert.throws(() => expandRange('a-Z'), RangeError);
});

test('rejects invalid input', () => {
  assert.throws(() => expandRange('1-'), RangeError);
  assert.throws(() => expandRange('hello'), RangeError);
  assert.throws(() => expandRange(''), RangeError);
});

test('rejects non-string input', () => {
  assert.throws(() => expandRange(5), TypeError);
});
