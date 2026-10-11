import assert from 'node:assert/strict';
import test from 'node:test';
import { rangeToRegex, rangeToRegExp } from '../src/range-to-regex.js';

test('converts the canonical 1-100 example', () => {
  assert.equal(rangeToRegex(1, 100), '([1-9]|(1[0-9]|[2-8][0-9]|9[0-9])|100)');
});

test('matches every number inside the range and nothing outside', () => {
  const regex = rangeToRegExp(1, 100);
  for (let n = 1; n <= 100; n += 1) {
    assert.ok(regex.test(String(n)), `expected ${n} to match`);
  }
  for (const n of [0, 101, 1000, 200]) {
    assert.ok(!regex.test(String(n)), `expected ${n} not to match`);
  }
});

test('is exact across many small ranges', () => {
  for (let min = 0; min <= 60; min += 3) {
    for (let max = min; max <= 60; max += 7) {
      const regex = rangeToRegExp(min, max);
      for (let n = 0; n <= 80; n += 1) {
        assert.equal(regex.test(String(n)), n >= min && n <= max, `range ${min}-${max}, value ${n}`);
      }
    }
  }
});

test('spans multiple digit lengths', () => {
  const regex = rangeToRegExp(8, 1234);
  for (const n of [8, 9, 10, 99, 100, 999, 1000, 1234]) {
    assert.ok(regex.test(String(n)), `expected ${n} to match`);
  }
  for (const n of [7, 1235, 9999]) {
    assert.ok(!regex.test(String(n)), `expected ${n} not to match`);
  }
});

test('rejects leading zeros', () => {
  const regex = rangeToRegExp(1, 100);
  assert.ok(!regex.test('01'));
  assert.ok(!regex.test('001'));
});

test('accepts swapped bounds', () => {
  assert.equal(rangeToRegex(100, 1), rangeToRegex(1, 100));
});

test('single value range matches only that value', () => {
  const regex = rangeToRegExp(42, 42);
  assert.ok(regex.test('42'));
  assert.ok(!regex.test('4'));
  assert.ok(!regex.test('421'));
});

test('rejects invalid input', () => {
  assert.throws(() => rangeToRegex(1.5, 10), TypeError);
  assert.throws(() => rangeToRegex(-1, 10), RangeError);
});
