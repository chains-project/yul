import { test } from 'node:test';
import assert from 'node:assert/strict';
import { expandRange } from '../src/expandRange.js';

test('ascending numeric range', () => {
  assert.deepEqual(expandRange('1-10'), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test('descending numeric range', () => {
  assert.deepEqual(expandRange('3-1'), [3, 2, 1]);
});

test('negative numbers', () => {
  assert.deepEqual(expandRange('-2-2'), [-2, -1, 0, 1, 2]);
  assert.deepEqual(expandRange('-1--3'), [-1, -2, -3]);
});

test('single-value range', () => {
  assert.deepEqual(expandRange('7-7'), [7]);
  assert.deepEqual(expandRange('q-q'), ['q']);
});

test('lowercase letter range', () => {
  const az = expandRange('a-z');
  assert.equal(az.length, 26);
  assert.equal(az[0], 'a');
  assert.equal(az[25], 'z');
});

test('uppercase and descending letter range', () => {
  assert.deepEqual(expandRange('E-A'), ['E', 'D', 'C', 'B', 'A']);
});

test('trims whitespace', () => {
  assert.deepEqual(expandRange('  1-3 '), [1, 2, 3]);
});

test('rejects invalid input', () => {
  assert.throws(() => expandRange('a-Z'), RangeError);
  assert.throws(() => expandRange('1-z'), SyntaxError);
  assert.throws(() => expandRange('abc'), SyntaxError);
  assert.throws(() => expandRange('1.5-3'), SyntaxError);
  assert.throws(() => expandRange(5), TypeError);
});
