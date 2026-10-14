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
  assert.deepEqual(expandRange('1--1'), [1, 0, -1]);
});

test('single-value range', () => {
  assert.deepEqual(expandRange('7-7'), [7]);
});

test('lowercase letter range', () => {
  const az = expandRange('a-z');
  assert.equal(az.length, 26);
  assert.equal(az[0], 'a');
  assert.equal(az[25], 'z');
});

test('uppercase and descending letter ranges', () => {
  assert.deepEqual(expandRange('A-D'), ['A', 'B', 'C', 'D']);
  assert.deepEqual(expandRange('d-a'), ['d', 'c', 'b', 'a']);
});

test('trims surrounding whitespace', () => {
  assert.deepEqual(expandRange(' 1-3 '), [1, 2, 3]);
});

test('rejects invalid input', () => {
  for (const bad of ['', '1', 'a-Z', '1-z', 'aa-zz', '1.5-3', '1-', 'abc']) {
    assert.throws(() => expandRange(bad), /Invalid range/, bad);
  }
  assert.throws(() => expandRange(5), TypeError);
});
