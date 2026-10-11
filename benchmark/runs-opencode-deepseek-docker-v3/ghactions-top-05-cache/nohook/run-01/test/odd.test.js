import test from 'node:test';
import assert from 'node:assert/strict';
import isOdd from 'is-odd';

test('detects odd numbers', () => {
  assert.equal(isOdd(3), true);
});

test('detects even numbers', () => {
  assert.equal(isOdd(4), false);
});
