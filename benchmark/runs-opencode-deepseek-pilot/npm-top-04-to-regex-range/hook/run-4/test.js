import test from 'node:test';
import assert from 'node:assert/strict';
import { rangeToRegex } from './index.js';

test('matches every number in 1-100 and nothing outside it', () => {
  const regex = rangeToRegex('1-100');

  for (let n = 1; n <= 100; n++) {
    assert.ok(regex.test(String(n)), `expected ${n} to match`);
  }

  for (const n of ['0', '101', '-1', '1.5', 'abc', '']) {
    assert.ok(!regex.test(n), `expected "${n}" not to match`);
  }
});

test('rejects malformed ranges', () => {
  assert.throws(() => rangeToRegex('nope'), /Invalid range/);
});
