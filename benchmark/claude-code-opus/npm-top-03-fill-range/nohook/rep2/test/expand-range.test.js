import { test } from 'node:test';
import assert from 'node:assert/strict';
import { expandRange } from '../src/expand-range.js';

test('ascending numbers', () => {
  assert.deepEqual(expandRange('1-10'), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test('descending numbers', () => {
  assert.deepEqual(expandRange('5-1'), [5, 4, 3, 2, 1]);
});

test('negative numbers', () => {
  assert.deepEqual(expandRange('-2-2'), [-2, -1, 0, 1, 2]);
  assert.deepEqual(expandRange('-1--3'), [-1, -2, -3]);
});

test('single value range', () => {
  assert.deepEqual(expandRange('7-7'), [7]);
  assert.deepEqual(expandRange('q-q'), ['q']);
});

test('zero padding is preserved', () => {
  assert.deepEqual(expandRange('08-11'), ['08', '09', '10', '11']);
  assert.deepEqual(expandRange('001-3'), ['001', '002', '003']);
});

test('lowercase letters', () => {
  assert.equal(expandRange('a-z').join(''), 'abcdefghijklmnopqrstuvwxyz');
});

test('uppercase and descending letters', () => {
  assert.deepEqual(expandRange('E-A'), ['E', 'D', 'C', 'B', 'A']);
});

test('step', () => {
  assert.deepEqual(expandRange('1-10', 3), [1, 4, 7, 10]);
  assert.deepEqual(expandRange('10-1', 4), [10, 6, 2]);
  assert.deepEqual(expandRange('a-g', 2), ['a', 'c', 'e', 'g']);
});

test('surrounding whitespace is ignored', () => {
  assert.deepEqual(expandRange(' 1-3 '), [1, 2, 3]);
});

test('invalid input throws', () => {
  for (const bad of ['', '1', 'a-Z', '1-z', 'aa-zz', '1.5-3', '1 - 3']) {
    assert.throws(() => expandRange(bad), SyntaxError, `expected "${bad}" to throw`);
  }
  assert.throws(() => expandRange(5), TypeError);
  assert.throws(() => expandRange('1-5', 0), RangeError);
  assert.throws(() => expandRange('1-5', 1.5), RangeError);
});
