'use strict';

const test = require('node:test');
const assert = require('node:assert');
const { parseRange, rangeToRegex } = require('../src/range-to-regex');

function assertExact(range, min, max) {
  const re = rangeToRegex(range);
  for (let n = min - 50; n <= max + 50; n++) {
    assert.strictEqual(re.test(String(n)), n >= min && n <= max, `${range}: ${n}`);
  }
}

test('1-100 matches exactly 1..100', () => assertExact('1-100', 1, 100));
test('0-9', () => assertExact('0-9', 0, 9));
test('17-4321', () => assertExact('17-4321', 17, 4321));
test('negative range', () => assertExact('-25--3', -25, -3));
test('range crossing zero', () => assertExact('-10-10', -10, 10));
test('single value', () => assertExact('42-42', 42, 42));
test('reversed bounds are swapped', () => assert.deepStrictEqual(parseRange('100-1'), [1, 100]));
test('rejects partial matches', () => {
  const re = rangeToRegex('1-100');
  for (const s of ['1000', '0', 'a5', '5a', '', '1.5']) assert.strictEqual(re.test(s), false, s);
});
test('invalid input throws', () => {
  for (const s of ['abc', '1-', '-', '1..100', '1-2-3']) assert.throws(() => parseRange(s), s);
});
