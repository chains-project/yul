'use strict';

const assert = require('assert');
const rangeToRegex = require('./index');

function matches(range, value) {
  return rangeToRegex(range).test(value);
}

assert.strictEqual(rangeToRegex('1-100').source, '^(?:[1-9]|[1-9][0-9]|100)$');

assert.strictEqual(matches('1-100', '1'), true);
assert.strictEqual(matches('1-100', '50'), true);
assert.strictEqual(matches('1-100', '100'), true);
assert.strictEqual(matches('1-100', '0'), false);
assert.strictEqual(matches('1-100', '101'), false);
assert.strictEqual(matches('1-100', '150'), false);

assert.strictEqual(matches('15-95', '14'), false);
assert.strictEqual(matches('15-95', '94'), true);
assert.strictEqual(matches('15-95', '96'), false);

assert.strictEqual(matches('-10-10', '-10'), true);
assert.strictEqual(matches('-10-10', '10'), true);
assert.strictEqual(matches('-10-10', '11'), false);

assert.throws(() => rangeToRegex('not-a-range'), TypeError);

console.log('All tests passed.');
