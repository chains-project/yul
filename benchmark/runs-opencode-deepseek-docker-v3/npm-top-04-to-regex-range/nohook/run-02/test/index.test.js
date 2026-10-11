import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  parseRange,
  rangeToRegex,
  rangeToRegExp,
} from '../src/index.js';

test('parses dash and dot-dot ranges', () => {
  assert.deepEqual(parseRange('1-100'), { min: 1, max: 100 });
  assert.deepEqual(parseRange(' 1 .. 100 '), { min: 1, max: 100 });
  assert.deepEqual(parseRange('-5-5'), { min: -5, max: 5 });
  assert.deepEqual(parseRange('-10..-1'), { min: -10, max: -1 });
});

test('rejects malformed ranges', () => {
  assert.throws(() => parseRange('1'), SyntaxError);
  assert.throws(() => parseRange('a-b'), SyntaxError);
});

test('generates a single expression for 1-100', () => {
  const source = rangeToRegex('1-100');
  assert.equal(source, '(?:[1-9]|[1-9][0-9]|100)');
});

test('matches every value inside the range', () => {
  const re = rangeToRegExp('1-100');
  for (let n = 1; n <= 100; n += 1) {
    assert.ok(re.test(String(n)), `expected ${n} to match`);
  }
});

test('rejects values outside the range', () => {
  const re = rangeToRegExp('1-100');
  for (const n of ['0', '101', '1000', '007', '-1', 'abc', '']) {
    assert.ok(!re.test(n), `expected ${n} not to match`);
  }
});

test('supports { min, max } input', () => {
  const re = rangeToRegExp({ min: 1, max: 100 });
  assert.ok(re.test('50'));
  assert.ok(!re.test('0'));
});

test('handles negative ranges', () => {
  const re = rangeToRegExp('-10..-1');
  assert.ok(re.test('-10'));
  assert.ok(re.test('-1'));
  assert.ok(!re.test('0'));
});

test('throws when min is greater than max', () => {
  assert.throws(() => rangeToRegex('100-1'), RangeError);
});
