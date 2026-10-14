import { test } from 'node:test';
import assert from 'node:assert/strict';
import { rangeToRegex } from './index.js';

const check = (range, min, max) => {
  const re = rangeToRegex(range);
  for (let n = min - 50; n <= max + 50; n++) {
    assert.equal(re.test(String(n)), n >= min && n <= max, `${range} vs ${n}`);
  }
};

test('1-100', () => check('1-100', 1, 100));
test('0-9', () => check('0-9', 0, 9));
test('17-4321', () => check('17-4321', 17, 4321));
test('negative bounds', () => check('-25-30', -25, 30));
test('reversed bounds', () => check('100-1', 1, 100));
test('rejects garbage', () => assert.throws(() => rangeToRegex('abc')));
test('no partial matches', () => assert.equal(rangeToRegex('1-100').test('1000'), false));
