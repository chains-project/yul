import { test } from 'node:test';
import assert from 'node:assert/strict';
import { expandRange } from '../src/expand-range.js';

test('expands ascending numeric ranges', () => {
  assert.deepEqual(expandRange('1-10'), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test('expands descending numeric ranges', () => {
  assert.deepEqual(expandRange('5-1'), [5, 4, 3, 2, 1]);
});

test('handles negative numbers', () => {
  assert.deepEqual(expandRange('-2-2'), [-2, -1, 0, 1, 2]);
  assert.deepEqual(expandRange('-1--3'), [-1, -2, -3]);
});

test('handles single-value ranges', () => {
  assert.deepEqual(expandRange('7-7'), [7]);
  assert.deepEqual(expandRange('q-q'), ['q']);
});

test('expands lowercase and uppercase letter ranges', () => {
  assert.equal(expandRange('a-z').join(''), 'abcdefghijklmnopqrstuvwxyz');
  assert.deepEqual(expandRange('C-A'), ['C', 'B', 'A']);
});

test('tolerates surrounding whitespace', () => {
  assert.deepEqual(expandRange(' 1 - 3 '), [1, 2, 3]);
});

test('rejects mixed-case letter ranges', () => {
  assert.throws(() => expandRange('a-Z'), RangeError);
});

test('rejects malformed input', () => {
  for (const bad of ['', '1-', 'a-10', 'ab-cd', '1..10', '1.5-3']) {
    assert.throws(() => expandRange(bad), SyntaxError, bad);
  }
  assert.throws(() => expandRange(5), TypeError);
});
