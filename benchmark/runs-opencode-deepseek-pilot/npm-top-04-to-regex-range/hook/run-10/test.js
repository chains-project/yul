'use strict';

const test = require('node:test');
const assert = require('node:assert');
const rangeToRegex = require('./index.js');

test('matches numbers within the range', () => {
  const regex = rangeToRegex('1-100');
  for (const n of [1, 5, 42, 99, 100]) {
    assert.ok(regex.test(String(n)), `${n} should match`);
  }
});

test('does not match numbers outside the range', () => {
  const regex = rangeToRegex('1-100');
  for (const n of [0, 101, 1000]) {
    assert.ok(!regex.test(String(n)), `${n} should not match`);
  }
});

test('supports negative ranges', () => {
  const regex = rangeToRegex('-10-10');
  assert.ok(regex.test('-10'));
  assert.ok(regex.test('0'));
  assert.ok(regex.test('10'));
  assert.ok(!regex.test('11'));
});

test('throws on invalid input', () => {
  assert.throws(() => rangeToRegex('abc'), TypeError);
});
