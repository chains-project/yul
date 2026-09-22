'use strict';

const test = require('node:test');
const assert = require('node:assert');
const toRegexRange = require('../index.js');

const matcher = pattern => new RegExp('^(?:' + pattern + ')$');

test('matches every number in a range', () => {
  const ranges = [
    [1, 100],
    [1, 10],
    [10, 20],
    [5, 5],
    [0, 9],
    [-5, 5],
    [-100, -1],
    [100, 200],
    [1, 1000],
    [42, 4200]
  ];

  for (const [min, max] of ranges) {
    const regex = matcher(toRegexRange(min, max));
    for (let n = min; n <= max; n++) {
      assert.ok(regex.test(String(n)), `expected ${toRegexRange(min, max)} to match ${n}`);
    }
  }
});

test('does not match numbers outside the range', () => {
  const ranges = [
    [1, 100],
    [10, 20],
    [-5, 5],
    [100, 200]
  ];

  for (const [min, max] of ranges) {
    const regex = matcher(toRegexRange(min, max));
    for (const n of [min - 1, max + 1, min - 100, max + 100]) {
      assert.ok(!regex.test(String(n)), `did not expect ${toRegexRange(min, max)} to match ${n}`);
    }
  }
});

test('returns the number when min equals max', () => {
  assert.strictEqual(toRegexRange(5, 5), '5');
  assert.strictEqual(toRegexRange(-7, -7), '-7');
});

test('wraps multi-part patterns by default', () => {
  assert.strictEqual(toRegexRange(1, 100), '(?:[1-9]|[1-9][0-9]|100)');
  assert.strictEqual(toRegexRange(1, 100, { wrap: false }), '[1-9]|[1-9][0-9]|100');
  assert.strictEqual(toRegexRange(1, 100, { capture: true }), '([1-9]|[1-9][0-9]|100)');
});

test('supports the shorthand option', () => {
  assert.strictEqual(toRegexRange(1, 100, { shorthand: true }), '(?:[1-9]|[1-9]\\d|100)');
});

test('handles zero padded ranges', () => {
  const pattern = toRegexRange('001', '100');
  const regex = matcher(pattern);
  for (let n = 1; n <= 100; n++) {
    const padded = String(n).padStart(3, '0');
    assert.ok(regex.test(padded), `expected ${pattern} to match ${padded}`);
  }
});

test('throws on invalid input', () => {
  assert.throws(() => toRegexRange('foo', 10), TypeError);
  assert.throws(() => toRegexRange(1, 'bar'), TypeError);
});
