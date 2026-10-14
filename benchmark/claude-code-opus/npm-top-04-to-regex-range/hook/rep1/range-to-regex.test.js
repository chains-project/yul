'use strict';

const test = require('node:test');
const assert = require('node:assert');
const { rangeToRegex } = require('./range-to-regex');

function checkRange(min, max, probeFrom, probeTo) {
  const re = rangeToRegex(`${min}-${max}`);
  for (let n = probeFrom; n <= probeTo; n++) {
    assert.strictEqual(re.test(String(n)), n >= min && n <= max, `${n} vs ${re}`);
  }
}

test('1-100 matches exactly 1..100', () => checkRange(1, 100, -50, 1000));
test('arbitrary range 37-4521', () => checkRange(37, 4521, 0, 10000));
test('negative range', () => checkRange(-25, 10, -100, 100));
test('reversed bounds are swapped', () => {
  assert.strictEqual(rangeToRegex('100-1').source, rangeToRegex('1-100').source);
});
test('rejects partial matches and junk', () => {
  const re = rangeToRegex('1-100');
  for (const s of ['0100', '1000', '50a', ' 50', '']) assert.ok(!re.test(s), s);
});
test('invalid input throws', () => {
  assert.throws(() => rangeToRegex('abc'));
  assert.throws(() => rangeToRegex('1-'));
});
