import { test } from 'node:test';
import assert from 'node:assert/strict';
import { expandRange } from '../src/expand-range.js';

test('expands a numeric range', () => {
  assert.deepEqual(expandRange('1-10'), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test('expands a lowercase alphabetic range', () => {
  assert.deepEqual(expandRange('a-z'), 'abcdefghijklmnopqrstuvwxyz'.split(''));
});

test('expands an uppercase alphabetic range', () => {
  assert.deepEqual(expandRange('A-E'), ['A', 'B', 'C', 'D', 'E']);
});

test('supports descending ranges', () => {
  assert.deepEqual(expandRange('5-1'), [5, 4, 3, 2, 1]);
});

test('supports negative numbers', () => {
  assert.deepEqual(expandRange('-2-2'), [-2, -1, 0, 1, 2]);
});

test('trims surrounding whitespace', () => {
  assert.deepEqual(expandRange('  3-6 '), [3, 4, 5, 6]);
});

test('treats a single value as a one-element range', () => {
  assert.deepEqual(expandRange('7'), [7]);
  assert.deepEqual(expandRange('b'), ['b']);
});

test('throws on empty input', () => {
  assert.throws(() => expandRange(''), /empty/i);
});

test('throws on an invalid range', () => {
  assert.throws(() => expandRange('a-1'), /Invalid range/);
});
