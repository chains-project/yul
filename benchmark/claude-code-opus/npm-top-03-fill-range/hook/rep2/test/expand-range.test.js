import { test } from 'node:test';
import assert from 'node:assert/strict';
import { expandRange } from '../src/expand-range.js';

test('expands numeric ranges', () => {
  assert.deepEqual(expandRange('1-10'), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
  assert.deepEqual(expandRange('3-3'), [3]);
});

test('expands descending numeric ranges', () => {
  assert.deepEqual(expandRange('5-1'), [5, 4, 3, 2, 1]);
});

test('handles negative numbers', () => {
  assert.deepEqual(expandRange('-2-2'), [-2, -1, 0, 1, 2]);
  assert.deepEqual(expandRange('-1--3'), [-1, -2, -3]);
});

test('expands letter ranges', () => {
  assert.equal(expandRange('a-z').length, 26);
  assert.deepEqual(expandRange('a-e'), ['a', 'b', 'c', 'd', 'e']);
  assert.deepEqual(expandRange('E-A'), ['E', 'D', 'C', 'B', 'A']);
});

test('supports a step', () => {
  assert.deepEqual(expandRange('1-10', { step: 3 }), [1, 4, 7, 10]);
  assert.deepEqual(expandRange('10-1', { step: 4 }), [10, 6, 2]);
  assert.deepEqual(expandRange('a-g', { step: 2 }), ['a', 'c', 'e', 'g']);
});

test('trims surrounding whitespace', () => {
  assert.deepEqual(expandRange(' 1-3 '), [1, 2, 3]);
});

test('rejects invalid input', () => {
  assert.throws(() => expandRange('1-z'), SyntaxError);
  assert.throws(() => expandRange('abc'), SyntaxError);
  assert.throws(() => expandRange(''), SyntaxError);
  assert.throws(() => expandRange('a-Z'), RangeError);
  assert.throws(() => expandRange('1-5', { step: 0 }), RangeError);
  assert.throws(() => expandRange('1-5', { step: 1.5 }), RangeError);
  assert.throws(() => expandRange(42), TypeError);
});
