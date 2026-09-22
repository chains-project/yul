'use strict';

const assert = require('node:assert');
const rangeToRegex = require('./index.js');

const regex = rangeToRegex('1-100');

for (let n = 1; n <= 100; n++) {
  assert.ok(regex.test(String(n)), `expected ${n} to match`);
}

for (const n of ['0', '101', '-1', '1000', 'abc', '1.5']) {
  assert.ok(!regex.test(n), `expected ${n} not to match`);
}

assert.ok(rangeToRegex('15-95').test('42'));
assert.ok(!rangeToRegex('15-95').test('96'));
assert.ok(rangeToRegex('-5-5').test('-3'));
assert.ok(!rangeToRegex('-5-5').test('6'));

assert.throws(() => rangeToRegex('nope'), /Invalid range/);
assert.throws(() => rangeToRegex(42), /Expected a string/);

console.log('All tests passed');
