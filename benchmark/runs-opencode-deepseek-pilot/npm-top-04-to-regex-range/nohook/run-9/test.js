'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');

const rangeToRegex = require('./index.js');

function matches(range, n) {
  const re = new RegExp(`^(?:${rangeToRegex(range)})$`);
  return re.test(String(n));
}

test('produces a single regex source for 1-100', () => {
  const source = rangeToRegex('1-100');
  assert.equal(typeof source, 'string');
  assert.equal(source, '(?:[1-9]|[1-9][0-9]|100)');
});

test('matches every number inside 1-100 and nothing outside', () => {
  for (let n = 1; n <= 100; n++) {
    assert.ok(matches('1-100', n), `${n} should match`);
  }

  assert.ok(!matches('1-100', 0), '0 should not match');
  assert.ok(!matches('1-100', 101), '101 should not match');
});

test('handles a single value range', () => {
  assert.equal(rangeToRegex('5-5'), '5');
  assert.ok(matches('5-5', 5));
  assert.ok(!matches('5-5', 6));
});

test('accepts an [min, max] array and whitespace', () => {
  assert.equal(rangeToRegex([1, 100]), '(?:[1-9]|[1-9][0-9]|100)');
  assert.ok(matches(' 10 - 20 ', 15));
});

test('supports negative ranges', () => {
  assert.ok(matches('-5-10', -5));
  assert.ok(matches('-5-10', 0));
  assert.ok(matches('-5-10', 10));
  assert.ok(!matches('-5-10', -6));
  assert.ok(!matches('-5-10', 11));
});

test('supports large ranges', () => {
  assert.ok(matches('1-65535', 65535));
  assert.ok(!matches('1-65535', 65536));
});

test('rejects invalid input', () => {
  assert.throws(() => rangeToRegex('abc'), TypeError);
  assert.throws(() => rangeToRegex('abc'), /Invalid numeric range/);
  assert.throws(() => rangeToRegex('100-1'), RangeError);
  assert.throws(() => rangeToRegex('100-1'), /greater than/);
});
