import { test } from 'node:test';
import assert from 'node:assert/strict';
import { expandRange } from '../src/expand-range.js';

test('expands ascending numeric ranges', () => {
  assert.deepEqual(expandRange('1-10'), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test('expands descending numeric ranges', () => {
  assert.deepEqual(expandRange('3-1'), [3, 2, 1]);
});

test('handles negative numbers', () => {
  assert.deepEqual(expandRange('-2-2'), [-2, -1, 0, 1, 2]);
  assert.deepEqual(expandRange('-1--3'), [-1, -2, -3]);
});

test('single-value range', () => {
  assert.deepEqual(expandRange('5-5'), [5]);
  assert.deepEqual(expandRange('q-q'), ['q']);
});

test('expands lowercase letter ranges', () => {
  const az = expandRange('a-z');
  assert.equal(az.length, 26);
  assert.equal(az[0], 'a');
  assert.equal(az[25], 'z');
});

test('expands uppercase and descending letter ranges', () => {
  assert.deepEqual(expandRange('A-C'), ['A', 'B', 'C']);
  assert.deepEqual(expandRange('c-a'), ['c', 'b', 'a']);
});

test('ignores surrounding whitespace', () => {
  assert.deepEqual(expandRange(' 1-3 '), [1, 2, 3]);
});

test('rejects mixed-case letter ranges', () => {
  assert.throws(() => expandRange('a-Z'), RangeError);
});

test('rejects invalid input', () => {
  for (const bad of ['', '1-', 'a-1', '1..10', 'aa-zz', '1.5-3']) {
    assert.throws(() => expandRange(bad), SyntaxError, `expected "${bad}" to throw`);
  }
  assert.throws(() => expandRange(10), TypeError);
});
