import test from 'node:test';
import assert from 'node:assert/strict';
import { rangeToRegex, rangeToRegexAnchored } from '../src/range-to-regex.js';

function assertRange(min, max, margin = 5) {
  const source = rangeToRegexAnchored(min, max);
  const re = new RegExp(source);
  for (let value = min - margin; value <= max + margin; value++) {
    const expected = value >= min && value <= max;
    assert.equal(
      re.test(String(value)),
      expected,
      `range ${min}-${max} (${source}) ${expected ? 'should' : 'should not'} match ${value}`
    );
  }
}

test('matches the documented 1-100 case', () => {
  const re = new RegExp(rangeToRegexAnchored(1, 100));
  assert.equal(re.test('1'), true);
  assert.equal(re.test('57'), true);
  assert.equal(re.test('100'), true);
  assert.equal(re.test('0'), false);
  assert.equal(re.test('101'), false);
});

test('handles single values', () => {
  assert.equal(rangeToRegex(5, 5), '5');
  assert.equal(rangeToRegex(-0, 0), '0');
  assertRange(7, 7);
});

test('handles single digit ranges', () => {
  assert.equal(rangeToRegex(0, 9), '\\d');
  assertRange(0, 9);
  assertRange(3, 8);
});

test('handles multi digit ranges', () => {
  assertRange(1, 100);
  assertRange(10, 99);
  assertRange(7, 13);
  assertRange(123, 456);
  assertRange(980, 1020);
  assertRange(1000, 9999);
});

test('handles ranges crossing digit boundaries', () => {
  assertRange(8, 12);
  assertRange(95, 105);
  assertRange(999, 1001);
  assertRange(9, 111);
});

test('handles negatives', () => {
  assertRange(-5, 5);
  assertRange(-100, -10);
  assertRange(-20, 30);
  assertRange(-456, -123);
});

test('normalizes reversed bounds', () => {
  assert.equal(rangeToRegex(100, 1), rangeToRegex(1, 100));
});

test('rejects non-integers', () => {
  assert.throws(() => rangeToRegex(1.5, 10), TypeError);
  assert.throws(() => rangeToRegex('1', 10), TypeError);
});
