import test from 'node:test';
import assert from 'node:assert/strict';
import { expandRange } from '../src/expandRange.js';

test('expands ascending numeric ranges', () => {
  assert.deepEqual(expandRange('1-10'), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test('expands descending numeric ranges', () => {
  assert.deepEqual(expandRange('3-1'), [3, 2, 1]);
});

test('expands multi-digit numeric ranges', () => {
  assert.deepEqual(expandRange('8-12'), [8, 9, 10, 11, 12]);
});

test('expands lowercase letter ranges', () => {
  assert.deepEqual(expandRange('a-z'), 'abcdefghijklmnopqrstuvwxyz'.split(''));
});

test('expands uppercase letter ranges', () => {
  assert.deepEqual(expandRange('A-E'), ['A', 'B', 'C', 'D', 'E']);
});

test('handles single-value ranges', () => {
  assert.deepEqual(expandRange('5-5'), [5]);
});

test('ignores surrounding whitespace', () => {
  assert.deepEqual(expandRange(' 2-4 '), [2, 3, 4]);
});

test('throws on invalid input', () => {
  assert.throws(() => expandRange('1-z'), /Invalid range/);
  assert.throws(() => expandRange('abc'), /Invalid range/);
  assert.throws(() => expandRange(42), TypeError);
});
