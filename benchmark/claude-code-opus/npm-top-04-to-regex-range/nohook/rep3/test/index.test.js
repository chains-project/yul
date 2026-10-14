import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseRange, rangeToRegex } from '../index.js';

function assertExact(range, lo, hi, margin = 50) {
  const re = rangeToRegex(range);
  for (let n = lo - margin; n <= hi + margin; n++) {
    assert.equal(re.test(String(n)), n >= lo && n <= hi, `${range} vs ${n}`);
  }
}

test('matches exactly 1-100', () => assertExact('1-100', 1, 100));
test('handles arbitrary bounds', () => assertExact('37-1234', 37, 1234));
test('handles single value', () => assertExact('42-42', 42, 42));
test('handles negative ranges', () => assertExact('-25--3', -25, -3));
test('handles ranges spanning zero', () => assertExact('-10-10', -10, 10));
test('normalizes reversed bounds', () => assert.deepEqual(parseRange('100-1'), [1, 100]));

test('rejects malformed input', () => {
  for (const bad of ['', 'abc', '1-', '1..100', '1-2-3']) {
    assert.throws(() => parseRange(bad), /Invalid range/);
  }
});

test('anchoring prevents partial matches', () => {
  assert.equal(rangeToRegex('1-100').test('150'), false);
  assert.equal(rangeToRegex('1-100', { anchored: false }).test('150'), true);
});
