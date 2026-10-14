'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { rangeToRegex, rangeToRegexSource } = require('../src/range-to-regex');

function assertExactRange(range, min, max, probeMin, probeMax) {
  const re = rangeToRegex(range);
  for (let n = probeMin; n <= probeMax; n++) {
    assert.equal(re.test(String(n)), n >= min && n <= max, `${range} vs ${n} (${re})`);
  }
}

test('1-100 matches exactly 1 through 100', () => {
  assertExactRange('1-100', 1, 100, -50, 1000);
});

test('handles single values and zero', () => {
  assertExactRange('0-0', 0, 0, -10, 10);
  assertExactRange('42-42', 42, 42, 0, 100);
});

test('handles negative ranges', () => {
  assertExactRange('-20-15', -20, 15, -100, 100);
  assertExactRange('-20--10', -20, -10, -100, 100);
});

test('swaps reversed bounds', () => {
  assertExactRange('100-1', 1, 100, 0, 200);
});

test('anchored pattern rejects partial matches', () => {
  const re = rangeToRegex('1-100');
  assert.equal(re.test('1000'), false);
  assert.equal(re.test('a5'), false);
  assert.equal(re.test('05'), false);
});

test('unanchored option returns the bare pattern', () => {
  assert.equal(rangeToRegexSource('1-9', { anchored: false }), '[1-9]');
});

test('rejects invalid input', () => {
  for (const bad of ['', '1', '1-', 'a-b', '1.5-3', '1-2-3']) {
    assert.throws(() => rangeToRegex(bad), /Invalid range/, bad);
  }
});
