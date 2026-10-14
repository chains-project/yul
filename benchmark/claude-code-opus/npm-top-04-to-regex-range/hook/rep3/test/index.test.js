'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { parseRange, rangeToRegex } = require('../index');

function assertExact(range, min, max, slack = 50) {
  const re = rangeToRegex(range);
  for (let n = min - slack; n <= max + slack; n++) {
    assert.equal(re.test(String(n)), n >= min && n <= max, `${range} vs ${n}`);
  }
}

test('1-100 matches exactly 1..100', () => assertExact('1-100', 1, 100));
test('0-255', () => assertExact('0-255', 0, 255));
test('odd boundaries 17-1234', () => assertExact('17-1234', 17, 1234));
test('negative ranges', () => assertExact('-20--5', -20, -5, 10));
test('range crossing zero', () => assertExact('-15-15', -15, 15));
test('single value', () => assertExact('42-42', 42, 42));
test('reversed bounds are normalized', () => assert.deepEqual(parseRange('100-1'), [1, 100]));

test('rejects partial matches and non-numbers', () => {
  const re = rangeToRegex('1-100');
  for (const s of ['', 'abc', '1000', '0100', '50a', ' 50', '5.5']) {
    assert.equal(re.test(s), false, JSON.stringify(s));
  }
});

test('rejects invalid input', () => {
  for (const bad of ['', '1', 'a-b', '1-', '1-2-3']) {
    assert.throws(() => parseRange(bad));
  }
});
