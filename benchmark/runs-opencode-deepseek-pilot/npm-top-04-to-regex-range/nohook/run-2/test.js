'use strict';

const assert = require('node:assert');
const { test } = require('node:test');

const rangeToRegex = require('./index.js');

test('matches numbers inside the range', () => {
  const re = rangeToRegex('1-100');

  for (const n of [1, 2, 42, 99, 100]) {
    assert.ok(re.test(String(n)), `expected ${n} to match`);
  }
});

test('does not match numbers outside the range', () => {
  const re = rangeToRegex('1-100');

  for (const n of [0, 101, 1000]) {
    assert.ok(!re.test(String(n)), `expected ${n} not to match`);
  }
});

test('does not match partial strings', () => {
  const re = rangeToRegex('1-100');

  assert.ok(!re.test('foo1'), 'expected "foo1" not to match');
  assert.ok(!re.test('100foo'), 'expected "100foo" not to match');
  assert.ok(!re.test('1.5'), 'expected "1.5" not to match');
});

test('accepts whitespace around the dash', () => {
  assert.ok(rangeToRegex(' 10 - 20 ').test('15'));
});

test('supports single-value and large ranges', () => {
  const single = rangeToRegex('5-5');
  assert.ok(single.test('5'));
  assert.ok(!single.test('6'));

  const large = rangeToRegex('1-65535');
  assert.ok(large.test('65535'));
  assert.ok(!large.test('65536'));
});

test('throws on invalid input', () => {
  assert.throws(() => rangeToRegex('abc'), TypeError);
  assert.throws(() => rangeToRegex('100-1'), RangeError);
});
